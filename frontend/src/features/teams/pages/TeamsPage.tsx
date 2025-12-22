import React, { useState } from 'react';
import { Card, Table, Button, Tag, Space, Typography, Avatar, Badge, Modal, Form, Input, Select, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, UserOutlined, PhoneOutlined, DeleteOutlined, UserAddOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  isOnCall: boolean;
}

interface Team {
  id: string;
  name: string;
  description: string;
  type: string;
  memberCount: number;
  members: TeamMember[];
  onCallPerson: string | null;
}

const initialTeams: Team[] = [
  {
    id: '1',
    name: 'Platform Engineering',
    description: 'Core infrastructure and platform services',
    type: 'engineering',
    memberCount: 8,
    members: [
      { id: '1', name: 'John Smith', email: 'john@example.com', role: 'Lead', isOnCall: true },
      { id: '2', name: 'Sarah Johnson', email: 'sarah@example.com', role: 'SRE', isOnCall: false },
    ],
    onCallPerson: 'John Smith',
  },
  {
    id: '2',
    name: 'Application Support',
    description: 'Application monitoring and support',
    type: 'support',
    memberCount: 12,
    members: [
      { id: '3', name: 'Mike Wilson', email: 'mike@example.com', role: 'Manager', isOnCall: false },
      { id: '4', name: 'Emily Davis', email: 'emily@example.com', role: 'Engineer', isOnCall: true },
    ],
    onCallPerson: 'Emily Davis',
  },
  {
    id: '3',
    name: 'Security Operations',
    description: 'Security monitoring and incident response',
    type: 'security',
    memberCount: 5,
    members: [
      { id: '5', name: 'Alex Chen', email: 'alex@example.com', role: 'Security Lead', isOnCall: true },
    ],
    onCallPerson: 'Alex Chen',
  },
  {
    id: '4',
    name: 'Database Administration',
    description: 'Database management and optimization',
    type: 'engineering',
    memberCount: 4,
    members: [
      { id: '6', name: 'Lisa Brown', email: 'lisa@example.com', role: 'DBA Lead', isOnCall: false },
    ],
    onCallPerson: null,
  },
  {
    id: '5',
    name: 'Network Operations',
    description: 'Network infrastructure and connectivity',
    type: 'operations',
    memberCount: 6,
    members: [
      { id: '7', name: 'Tom Anderson', email: 'tom@example.com', role: 'Network Engineer', isOnCall: true },
    ],
    onCallPerson: 'Tom Anderson',
  },
];

const typeColors: Record<string, string> = {
  engineering: 'blue',
  support: 'green',
  security: 'red',
  operations: 'purple',
};

const roleOptions = ['Lead', 'Manager', 'Engineer', 'SRE', 'Security Lead', 'DBA Lead', 'Network Engineer', 'Analyst'];

const TeamsPage: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>(initialTeams);
  const [isCreateTeamModalOpen, setIsCreateTeamModalOpen] = useState(false);
  const [isEditTeamModalOpen, setIsEditTeamModalOpen] = useState(false);
  const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false);
  const [isOnCallModalOpen, setIsOnCallModalOpen] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [form] = Form.useForm();
  const [memberForm] = Form.useForm();

  const handleCreateTeam = () => {
    form.validateFields().then((values) => {
      const newTeam: Team = {
        id: String(Date.now()),
        name: values.name,
        description: values.description,
        type: values.type,
        memberCount: 0,
        members: [],
        onCallPerson: null,
      };
      setTeams([...teams, newTeam]);
      message.success(`Team "${values.name}" created successfully`);
      setIsCreateTeamModalOpen(false);
      form.resetFields();
    });
  };

  const handleEditTeam = () => {
    form.validateFields().then((values) => {
      setTeams(teams.map(t =>
        t.id === selectedTeam?.id
          ? { ...t, name: values.name, description: values.description, type: values.type }
          : t
      ));
      message.success(`Team "${values.name}" updated successfully`);
      setIsEditTeamModalOpen(false);
      setSelectedTeam(null);
    });
  };

  const handleDeleteTeam = (team: Team) => {
    setTeams(teams.filter(t => t.id !== team.id));
    message.success(`Team "${team.name}" deleted`);
  };

  const handleAddMember = () => {
    memberForm.validateFields().then((values) => {
      const newMember: TeamMember = {
        id: String(Date.now()),
        name: values.name,
        email: values.email,
        role: values.role,
        isOnCall: false,
      };
      setTeams(teams.map(t =>
        t.id === selectedTeam?.id
          ? { ...t, members: [...t.members, newMember], memberCount: t.memberCount + 1 }
          : t
      ));
      message.success(`${values.name} added to ${selectedTeam?.name}`);
      setIsAddMemberModalOpen(false);
      memberForm.resetFields();
      setSelectedTeam(null);
    });
  };

  const handleSetOnCall = (member: TeamMember) => {
    setTeams(teams.map(t =>
      t.id === selectedTeam?.id
        ? {
            ...t,
            onCallPerson: member.name,
            members: t.members.map(m => ({ ...m, isOnCall: m.id === member.id })),
          }
        : t
    ));
    message.success(`${member.name} is now on-call for ${selectedTeam?.name}`);
    setIsOnCallModalOpen(false);
    setSelectedTeam(null);
  };

  const handleRemoveMember = (teamId: string, memberId: string, memberName: string) => {
    setTeams(teams.map(t =>
      t.id === teamId
        ? {
            ...t,
            members: t.members.filter(m => m.id !== memberId),
            memberCount: t.memberCount - 1,
            onCallPerson: t.onCallPerson === memberName ? null : t.onCallPerson,
          }
        : t
    ));
    message.success(`${memberName} removed from team`);
  };

  const openEditModal = (team: Team) => {
    setSelectedTeam(team);
    form.setFieldsValue({
      name: team.name,
      description: team.description,
      type: team.type,
    });
    setIsEditTeamModalOpen(true);
  };

  const openAddMemberModal = (team: Team) => {
    setSelectedTeam(team);
    setIsAddMemberModalOpen(true);
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
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#888' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag color={typeColors[type]}>{type.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Members',
      dataIndex: 'memberCount',
      key: 'memberCount',
      render: (count, record) => (
        <Space>
          <Avatar.Group maxCount={3}>
            {record.members.slice(0, 4).map((m, i) => (
              <Avatar key={m.id} icon={<UserOutlined />} style={{ backgroundColor: `hsl(${i * 60}, 70%, 50%)` }} />
            ))}
          </Avatar.Group>
          <span>{count} members</span>
        </Space>
      ),
    },
    {
      title: 'On-Call',
      dataIndex: 'onCallPerson',
      key: 'onCallPerson',
      render: (person) => person ? (
        <Badge status="success" text={person} />
      ) : (
        <Badge status="default" text="Not assigned" />
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="text" icon={<UserAddOutlined />} onClick={() => openAddMemberModal(record)} title="Add Member" />
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
          pagination={{ pageSize: 10 }}
          expandable={{
            expandedRowRender: (record) => (
              <Table
                columns={[
                  { title: 'Name', dataIndex: 'name', key: 'name' },
                  { title: 'Email', dataIndex: 'email', key: 'email' },
                  { title: 'Role', dataIndex: 'role', key: 'role' },
                  {
                    title: 'On-Call',
                    dataIndex: 'isOnCall',
                    key: 'isOnCall',
                    render: (isOnCall) => isOnCall ? <Badge status="success" text="Yes" /> : <Badge status="default" text="No" />,
                  },
                  {
                    title: 'Actions',
                    key: 'actions',
                    render: (_, member) => (
                      <Popconfirm
                        title="Remove Member"
                        description={`Remove ${member.name} from this team?`}
                        onConfirm={() => handleRemoveMember(record.id, member.id, member.name)}
                        okText="Yes"
                        cancelText="No"
                      >
                        <Button type="text" danger size="small" icon={<DeleteOutlined />}>Remove</Button>
                      </Popconfirm>
                    ),
                  },
                ]}
                dataSource={record.members}
                rowKey="id"
                pagination={false}
                size="small"
              />
            ),
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

      {/* Add Member Modal */}
      <Modal
        title={`Add Member to ${selectedTeam?.name}`}
        open={isAddMemberModalOpen}
        onOk={handleAddMember}
        onCancel={() => { setIsAddMemberModalOpen(false); memberForm.resetFields(); setSelectedTeam(null); }}
        okText="Add"
      >
        <Form form={memberForm} layout="vertical">
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Please enter member name' }]}>
            <Input placeholder="Enter member name" />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email', message: 'Please enter a valid email' }]}>
            <Input placeholder="Enter email address" />
          </Form.Item>
          <Form.Item name="role" label="Role" rules={[{ required: true, message: 'Please select a role' }]}>
            <Select placeholder="Select role">
              {roleOptions.map(r => <Select.Option key={r} value={r}>{r}</Select.Option>)}
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
        {selectedTeam?.members.length ? (
          <div>
            <Text type="secondary" style={{ marginBottom: 16, display: 'block' }}>Select a team member to set as on-call:</Text>
            {selectedTeam.members.map(member => (
              <Card
                key={member.id}
                size="small"
                hoverable
                style={{ marginBottom: 8, cursor: 'pointer' }}
                onClick={() => handleSetOnCall(member)}
              >
                <Space>
                  <Avatar icon={<UserOutlined />} />
                  <div>
                    <Text strong>{member.name}</Text>
                    {member.isOnCall && <Tag color="green" style={{ marginLeft: 8 }}>Current</Tag>}
                    <div><Text type="secondary" style={{ fontSize: 12 }}>{member.role}</Text></div>
                  </div>
                </Space>
              </Card>
            ))}
          </div>
        ) : (
          <Text type="secondary">No members in this team. Add members first.</Text>
        )}
      </Modal>
    </div>
  );
};

export default TeamsPage;
