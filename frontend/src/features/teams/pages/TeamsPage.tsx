import React, { useState } from 'react';
import { Card, Table, Button, Tag, Space, Typography, Avatar, Badge, Modal, Form, Input, Select, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, UserOutlined, PhoneOutlined, DeleteOutlined, UserAddOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useGetTeamsQuery,
  useCreateTeamMutation,
  useUpdateTeamMutation,
  useDeleteTeamMutation,
  useGetTeamMembersQuery,
  useUpdateTeamMemberMutation,
  useRemoveTeamMemberMutation,
  Team,
  TeamMember,
} from '../../../store/api/teamsApi';

const { Title, Text } = Typography;

const typeColors: Record<string, string> = {
  engineering: 'blue',
  support: 'green',
  security: 'red',
  operations: 'purple',
};

const TeamsPage: React.FC = () => {
  const { data: teamsData, isLoading } = useGetTeamsQuery({ skip: 0, limit: 100 });
  const [createTeam] = useCreateTeamMutation();
  const [updateTeam] = useUpdateTeamMutation();
  const [deleteTeam] = useDeleteTeamMutation();
  const [updateTeamMember] = useUpdateTeamMemberMutation();
  const [removeTeamMember] = useRemoveTeamMemberMutation();

  const [isCreateTeamModalOpen, setIsCreateTeamModalOpen] = useState(false);
  const [isEditTeamModalOpen, setIsEditTeamModalOpen] = useState(false);
  const [isOnCallModalOpen, setIsOnCallModalOpen] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [form] = Form.useForm();

  const teams = teamsData?.items || [];

  const handleCreateTeam = async () => {
    try {
      const values = await form.validateFields();
      await createTeam({
        name: values.name,
        description: values.description,
        team_type: values.type,
      }).unwrap();
      message.success(`Team "${values.name}" created successfully`);
      setIsCreateTeamModalOpen(false);
      form.resetFields();
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to create team');
    }
  };

  const handleEditTeam = async () => {
    if (!selectedTeam) return;
    try {
      const values = await form.validateFields();
      await updateTeam({
        id: selectedTeam.id,
        data: {
          name: values.name,
          description: values.description,
          team_type: values.type,
        },
      }).unwrap();
      message.success(`Team "${values.name}" updated successfully`);
      setIsEditTeamModalOpen(false);
      setSelectedTeam(null);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to update team');
    }
  };

  const handleDeleteTeam = async (team: Team) => {
    try {
      await deleteTeam(team.id).unwrap();
      message.success(`Team "${team.name}" deleted`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to delete team');
    }
  };

  const handleSetOnCall = async (member: TeamMember) => {
    if (!selectedTeam) return;
    try {
      await updateTeamMember({
        teamId: selectedTeam.id,
        memberId: member.id,
        data: { is_on_call: true },
      }).unwrap();
      message.success(`${member.name} is now on-call for ${selectedTeam.name}`);
      setIsOnCallModalOpen(false);
      setSelectedTeam(null);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to set on-call');
    }
  };

  const handleRemoveMember = async (teamId: string, memberId: string, memberName: string) => {
    try {
      await removeTeamMember({ teamId, memberId }).unwrap();
      message.success(`${memberName} removed from team`);
    } catch (error: any) {
      message.error(error?.data?.detail || 'Failed to remove member');
    }
  };

  const openEditModal = (team: Team) => {
    setSelectedTeam(team);
    form.setFieldsValue({
      name: team.name,
      description: team.description,
      type: team.team_type,
    });
    setIsEditTeamModalOpen(true);
  };

  const openOnCallModal = (team: Team) => {
    setSelectedTeam(team);
    setIsOnCallModalOpen(true);
  };

  const columns: ColumnsType<Team> = [
    {
      title: 'Team',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Team) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#888' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'team_type',
      key: 'team_type',
      render: (type: string) => (
        <Tag color={typeColors[type]}>{type.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Members',
      dataIndex: 'member_count',
      key: 'member_count',
      render: (count: number) => (
        <Space>
          <Avatar.Group maxCount={3}>
            {Array.from({ length: Math.min(count, 4) }).map((_, i) => (
              <Avatar key={i} icon={<UserOutlined />} style={{ backgroundColor: `hsl(${i * 60}, 70%, 50%)` }} />
            ))}
          </Avatar.Group>
          <span>{count} members</span>
        </Space>
      ),
    },
    {
      title: 'On-Call',
      dataIndex: 'on_call_person',
      key: 'on_call_person',
      render: (person: string | null) => person ? (
        <Badge status="success" text={person} />
      ) : (
        <Badge status="default" text="Not assigned" />
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Team) => (
        <Space>
          <Button type="text" icon={<PhoneOutlined />} onClick={() => openOnCallModal(record)} title="Set On-Call" />
          <Button type="text" icon={<EditOutlined />} onClick={() => openEditModal(record)} title="Edit Team" />
          <Popconfirm
            title="Delete Team"
            description={`Are you sure you want to delete "${record.name}"?`}
            onConfirm={() => handleDeleteTeam(record)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="text" danger icon={<DeleteOutlined />} title="Delete Team" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0 }}>Teams</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsCreateTeamModalOpen(true)}>
          Create Team
        </Button>
      </div>

      <Card>
        <Table
          columns={columns}
          dataSource={teams}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 10 }}
          expandable={{
            expandedRowRender: (record) => <TeamMembersTable teamId={record.id} onRemoveMember={handleRemoveMember} />,
          }}
        />
      </Card>

      {/* Create Team Modal */}
      <Modal
        title="Create New Team"
        open={isCreateTeamModalOpen}
        onOk={handleCreateTeam}
        onCancel={() => { setIsCreateTeamModalOpen(false); form.resetFields(); }}
        okText="Create"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Team Name" rules={[{ required: true, message: 'Please enter a team name' }]}>
            <Input placeholder="Enter team name" />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true, message: 'Please enter a description' }]}>
            <Input.TextArea rows={2} placeholder="Describe the team's responsibilities" />
          </Form.Item>
          <Form.Item name="type" label="Type" rules={[{ required: true, message: 'Please select a type' }]}>
            <Select placeholder="Select team type">
              <Select.Option value="engineering">Engineering</Select.Option>
              <Select.Option value="support">Support</Select.Option>
              <Select.Option value="security">Security</Select.Option>
              <Select.Option value="operations">Operations</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Edit Team Modal */}
      <Modal
        title="Edit Team"
        open={isEditTeamModalOpen}
        onOk={handleEditTeam}
        onCancel={() => { setIsEditTeamModalOpen(false); setSelectedTeam(null); }}
        okText="Save"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Team Name" rules={[{ required: true, message: 'Please enter a team name' }]}>
            <Input placeholder="Enter team name" />
          </Form.Item>
          <Form.Item name="description" label="Description" rules={[{ required: true, message: 'Please enter a description' }]}>
            <Input.TextArea rows={2} placeholder="Describe the team's responsibilities" />
          </Form.Item>
          <Form.Item name="type" label="Type" rules={[{ required: true, message: 'Please select a type' }]}>
            <Select placeholder="Select team type">
              <Select.Option value="engineering">Engineering</Select.Option>
              <Select.Option value="support">Support</Select.Option>
              <Select.Option value="security">Security</Select.Option>
              <Select.Option value="operations">Operations</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Set On-Call Modal */}
      <Modal
        title={`Set On-Call for ${selectedTeam?.name}`}
        open={isOnCallModalOpen}
        onCancel={() => { setIsOnCallModalOpen(false); setSelectedTeam(null); }}
        footer={null}
      >
        {selectedTeam && <OnCallSelector teamId={selectedTeam.id} onSelect={handleSetOnCall} />}
      </Modal>
    </div>
  );
};

// Separate component for team members table
const TeamMembersTable: React.FC<{ teamId: string; onRemoveMember: (teamId: string, memberId: string, memberName: string) => void }> = ({ teamId, onRemoveMember }) => {
  const { data: membersData } = useGetTeamMembersQuery(teamId);
  const members = membersData?.items || [];

  const columns: ColumnsType<TeamMember> = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Role', dataIndex: 'role', key: 'role' },
    {
      title: 'On-Call',
      dataIndex: 'is_on_call',
      key: 'is_on_call',
      render: (isOnCall: boolean) => isOnCall ? <Badge status="success" text="Yes" /> : <Badge status="default" text="No" />,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, member: TeamMember) => (
        <Popconfirm
          title="Remove Member"
          description={`Remove ${member.name} from this team?`}
          onConfirm={() => onRemoveMember(teamId, member.id, member.name)}
          okText="Yes"
          cancelText="No"
        >
          <Button type="text" danger size="small" icon={<DeleteOutlined />}>Remove</Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={members}
      rowKey="id"
      pagination={false}
      size="small"
    />
  );
};

// Separate component for on-call selector
const OnCallSelector: React.FC<{ teamId: string; onSelect: (member: TeamMember) => void }> = ({ teamId, onSelect }) => {
  const { data: membersData } = useGetTeamMembersQuery(teamId);
  const members = membersData?.items || [];

  if (members.length === 0) {
    return <Text type="secondary">No members in this team. Add members first.</Text>;
  }

  return (
    <div>
      <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>Select a team member to set as on-call:</Text>
      {members.map(member => (
        <Card
          key={member.id}
          size="small"
          hoverable
          style={{ marginBottom: 8, cursor: 'pointer' }}
          onClick={() => onSelect(member)}
        >
          <Space>
            <Avatar icon={<UserOutlined />} />
            <div>
              <Text strong>{member.name}</Text>
              {member.is_on_call && <Tag color="green" style={{ marginLeft: 8 }}>Current</Tag>}
              <div><Text type="secondary" style={{ fontSize: 12 }}>{member.role}</Text></div>
            </div>
          </Space>
        </Card>
      ))}
    </div>
  );
};

export default TeamsPage;
