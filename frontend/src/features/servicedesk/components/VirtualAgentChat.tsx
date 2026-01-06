import React, { useState, useEffect, useRef } from 'react';
import {
    Card,
    Input,
    Button,
    List,
    Avatar,
    Typography,
    Space,
    Tag,
    Spin,
    message,
    Tooltip,
    Badge,
    Divider,
} from 'antd';
import {
    SendOutlined,
    RobotOutlined,
    UserOutlined,
    ClockCircleOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    BookOutlined,
    ThunderboltOutlined,
} from '@ant-design/icons';
import { useStartConversationMutation, useSendMessageMutation } from '../../../store/api/virtualAgentApi';

const { Text, Title } = Typography;
const { TextArea } = Input;

interface Message {
    id: string;
    type: 'user' | 'agent' | 'system';
    content: string;
    sender_name?: string;
    timestamp: string;
    ai_confidence?: number;
    kb_articles?: string[];
    actions?: string[];
}

interface VirtualAgentChatProps {
    onEscalate?: (conversationId: string) => void;
    onClose?: () => void;
}

const VirtualAgentChat: React.FC<VirtualAgentChatProps> = ({ onEscalate, onClose }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [isStarted, setIsStarted] = useState(false);
    const [subject, setSubject] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const [startConversation] = useStartConversationMutation();
    const [sendMessage] = useSendMessageMutation();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleStartConversation = async () => {
        if (!subject.trim() || !inputValue.trim()) {
            message.error('Please provide both a subject and your initial message');
            return;
        }

        setIsLoading(true);
        try {
            const result = await startConversation({
                subject: subject.trim(),
                initial_message: inputValue.trim(),
            }).unwrap();

            setConversationId(result.conversation_id);
            setMessages(result.messages || []);
            setIsStarted(true);
            setInputValue('');
            setSubject('');
            message.success('Conversation started with AI Assistant');
        } catch (error) {
            console.error('Failed to start conversation:', error);
            message.error('Failed to start conversation. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSendMessage = async () => {
        if (!inputValue.trim() || !conversationId) return;

        const userMessage: Message = {
            id: `temp-${Date.now()}`,
            type: 'user',
            content: inputValue.trim(),
            sender_name: 'You',
            timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, userMessage]);
        const messageContent = inputValue.trim();
        setInputValue('');
        setIsLoading(true);

        try {
            const result = await sendMessage({
                conversation_id: conversationId,
                message: messageContent,
            }).unwrap();

            // Remove temporary message and add actual messages
            setMessages(prev => {
                const filtered = prev.filter(msg => msg.id !== userMessage.id);
                return [
                    ...filtered,
                    {
                        id: `user-${Date.now()}`,
                        type: 'user',
                        content: messageContent,
                        sender_name: 'You',
                        timestamp: new Date().toISOString(),
                    },
                    {
                        id: `agent-${Date.now()}`,
                        type: 'agent',
                        content: result.response,
                        sender_name: 'AI Assistant',
                        timestamp: new Date().toISOString(),
                        ai_confidence: result.confidence,
                        kb_articles: result.kb_articles,
                        actions: result.actions_executed,
                    },
                ];
            });

            // Handle escalation
            if (result.escalated && onEscalate) {
                message.info('Your request has been escalated to a human agent');
                onEscalate(conversationId);
            }

            // Show actions taken
            if (result.actions_executed && result.actions_executed.length > 0) {
                message.success(`Actions completed: ${result.actions_executed.join(', ')}`);
            }
        } catch (error) {
            console.error('Failed to send message:', error);
            message.error('Failed to send message. Please try again.');
            // Remove the temporary message on error
            setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (isStarted) {
                handleSendMessage();
            } else {
                handleStartConversation();
            }
        }
    };

    const renderMessage = (msg: Message) => {
        const isUser = msg.type === 'user';
        const isSystem = msg.type === 'system';

        return (
            <div
                key={msg.id}
                style={{
                    display: 'flex',
                    justifyContent: isUser ? 'flex-end' : 'flex-start',
                    marginBottom: 16,
                }}
            >
                <div
                    style={{
                        maxWidth: '70%',
                        display: 'flex',
                        flexDirection: isUser ? 'row-reverse' : 'row',
                        alignItems: 'flex-start',
                        gap: 8,
                    }}
                >
                    <Avatar
                        icon={isUser ? <UserOutlined /> : isSystem ? <ExclamationCircleOutlined /> : <RobotOutlined />}
                        style={{
                            backgroundColor: isUser ? '#1890ff' : isSystem ? '#faad14' : '#52c41a',
                        }}
                    />
                    <div
                        style={{
                            backgroundColor: isUser ? '#1890ff' : isSystem ? '#fff2e8' : '#f6ffed',
                            color: isUser ? 'white' : 'black',
                            padding: '8px 12px',
                            borderRadius: 8,
                            border: isSystem ? '1px solid #ffd591' : 'none',
                        }}
                    >
                        <div style={{ marginBottom: 4 }}>
                            <Text
                                style={{
                                    fontSize: '12px',
                                    opacity: 0.8,
                                    color: isUser ? 'rgba(255,255,255,0.8)' : 'rgba(0,0,0,0.6)',
                                }}
                            >
                                {msg.sender_name} • {new Date(msg.timestamp).toLocaleTimeString()}
                            </Text>
                        </div>
                        <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>

                        {/* AI Confidence and Actions */}
                        {!isUser && !isSystem && (
                            <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                                {msg.ai_confidence && (
                                    <Tooltip title={`AI Confidence: ${(msg.ai_confidence * 100).toFixed(0)}%`}>
                                        <Tag
                                            icon={<CheckCircleOutlined />}
                                            color={msg.ai_confidence > 0.8 ? 'green' : msg.ai_confidence > 0.6 ? 'orange' : 'red'}
                                            size="small"
                                        >
                                            {(msg.ai_confidence * 100).toFixed(0)}%
                                        </Tag>
                                    </Tooltip>
                                )}

                                {msg.kb_articles && msg.kb_articles.length > 0 && (
                                    <Tooltip title="Knowledge Base articles referenced">
                                        <Tag icon={<BookOutlined />} color="blue" size="small">
                                            {msg.kb_articles.length} KB articles
                                        </Tag>
                                    </Tooltip>
                                )}

                                {msg.actions && msg.actions.length > 0 && (
                                    <Tooltip title={`Actions: ${msg.actions.join(', ')}`}>
                                        <Tag icon={<ThunderboltOutlined />} color="purple" size="small">
                                            {msg.actions.length} actions
                                        </Tag>
                                    </Tooltip>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    };

    return (
        <Card
            title={
                <Space>
                    <RobotOutlined style={{ color: '#52c41a' }} />
                    <Title level={4} style={{ margin: 0 }}>
                        AI Assistant
                    </Title>
                    {conversationId && (
                        <Badge status="processing" text="Active" />
                    )}
                </Space>
            }
            extra={
                onClose && (
                    <Button type="text" onClick={onClose}>
                        Close
                    </Button>
                )
            }
            style={{ height: '600px', display: 'flex', flexDirection: 'column' }}
            bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}
        >
            {!isStarted ? (
                // Initial conversation setup
                <div style={{ padding: 24, flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <div style={{ textAlign: 'center', marginBottom: 24 }}>
                        <RobotOutlined style={{ fontSize: 48, color: '#52c41a', marginBottom: 16 }} />
                        <Title level={3}>Hi! I'm your AI Assistant</Title>
                        <Text type="secondary">
                            I can help you with password resets, account issues, software requests, and more.
                            What can I help you with today?
                        </Text>
                    </div>

                    <Space direction="vertical" size="large" style={{ width: '100%' }}>
                        <div>
                            <Text strong>Subject:</Text>
                            <Input
                                placeholder="Brief description of your issue (e.g., 'Password Reset')"
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                style={{ marginTop: 4 }}
                            />
                        </div>

                        <div>
                            <Text strong>How can I help you?</Text>
                            <TextArea
                                placeholder="Describe your issue in detail..."
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyPress={handleKeyPress}
                                rows={4}
                                style={{ marginTop: 4 }}
                            />
                        </div>

                        <Button
                            type="primary"
                            icon={<SendOutlined />}
                            onClick={handleStartConversation}
                            loading={isLoading}
                            disabled={!subject.trim() || !inputValue.trim()}
                            size="large"
                            block
                        >
                            Start Conversation
                        </Button>
                    </Space>
                </div>
            ) : (
                // Active conversation
                <>
                    {/* Messages Area */}
                    <div
                        style={{
                            flex: 1,
                            padding: '16px 24px',
                            overflowY: 'auto',
                            backgroundColor: '#fafafa',
                        }}
                    >
                        {messages.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: 40 }}>
                                <Spin size="large" />
                                <div style={{ marginTop: 16 }}>
                                    <Text type="secondary">Starting conversation...</Text>
                                </div>
                            </div>
                        ) : (
                            messages.map(renderMessage)
                        )}

                        {isLoading && (
                            <div style={{ textAlign: 'center', padding: 16 }}>
                                <Spin />
                                <Text type="secondary" style={{ marginLeft: 8 }}>
                                    AI is thinking...
                                </Text>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    <Divider style={{ margin: 0 }} />

                    {/* Input Area */}
                    <div style={{ padding: 16 }}>
                        <Space.Compact style={{ width: '100%' }}>
                            <TextArea
                                placeholder="Type your message..."
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyPress={handleKeyPress}
                                disabled={isLoading}
                                autoSize={{ minRows: 1, maxRows: 4 }}
                                style={{ flex: 1 }}
                            />
                            <Button
                                type="primary"
                                icon={<SendOutlined />}
                                onClick={handleSendMessage}
                                loading={isLoading}
                                disabled={!inputValue.trim()}
                            >
                                Send
                            </Button>
                        </Space.Compact>

                        <div style={{ marginTop: 8, textAlign: 'center' }}>
                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                <ClockCircleOutlined /> Press Enter to send, Shift+Enter for new line
                            </Text>
                        </div>
                    </div>
                </>
            )}
        </Card>
    );
};

export default VirtualAgentChat;