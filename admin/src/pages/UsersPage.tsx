import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { User, Role } from '../types';
import { 
  Search, 
  Plus, 
  Shield, 
  User as UserIcon,
  Eye,
  Trash2,
  Users,
  UserCheck,
  UserX,
  MessageSquare
} from 'lucide-react';

interface UserWithRoles extends User {
  roles: Role[];
  permissions: string[];
  total_permissions: number;
  is_active: boolean;
}

const UsersPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState<UserWithRoles | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showRoleModal, setShowRoleModal] = useState(false);

  const [usersData, setUsersData] = useState<any>(null);
  const [rolesData, setRolesData] = useState<any>(null);
  const [statsData, setStatsData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Make requests sequentially to avoid race conditions
        console.log('Fetching users...');
        const users = await apiService.getUsers({
          search: searchTerm || undefined,
          role: roleFilter || undefined,
          is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined
        }, 1, 20);
        console.log('Users fetched successfully:', users);
        
        console.log('Fetching roles...');
        const roles = await apiService.getAvailableRoles();
        console.log('Roles fetched successfully:', roles);
        
        console.log('Fetching stats...');
        const stats = await apiService.getUserStats();
        console.log('Stats fetched successfully:', stats);
        
        setUsersData(users);
        setRolesData(roles);
        setStatsData(stats);
      } catch (err: any) {
        console.error('Error fetching data:', err);
        setError(err.message || 'Failed to load data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [searchTerm, roleFilter, statusFilter]);

  const handleAssignRole = async (userId: number, roleName: string) => {
    try {
      await apiService.assignRole(userId, roleName);
      // Refresh data
      const users = await apiService.getUsers({
        search: searchTerm || undefined,
        role: roleFilter || undefined,
        is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined
      }, 1, 20);
      setUsersData(users);
      setShowRoleModal(false);
      alert('Role assigned successfully');
    } catch (err: any) {
      alert(err.message || 'Failed to assign role');
    }
  };

  const handleMessageUser = (user: UserWithRoles) => {
    // Navigate to messages page with the selected user
    window.location.href = `/messages?user=${user.id}`;
  };

  const handleRemoveRole = async (userId: number, roleName: string) => {
    if (window.confirm(`Are you sure you want to remove the ${roleName} role from this user?`)) {
      try {
        await apiService.removeRole(userId, roleName);
        // Refresh data
        const users = await apiService.getUsers({
          search: searchTerm || undefined,
          role: roleFilter || undefined,
          is_active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined
        }, 1, 20);
        setUsersData(users);
        alert('Role removed successfully');
      } catch (err: any) {
        alert(err.message || 'Failed to remove role');
      }
    }
  };

  const handleViewUser = (user: UserWithRoles) => {
    setSelectedUser(user);
    setShowUserModal(true);
  };

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-secondary-900">Users</h1>
          <p className="text-secondary-600">Manage registered users and their activity</p>
        </div>
        <div className="card">
          <div className="card-content">
            <div className="text-center py-12">
              <p className="text-red-500">Error loading users: {error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-secondary-900">Users</h1>
        <p className="text-secondary-600">Manage registered users and their activity</p>
      </div>

      {/* Stats Cards */}
      {statsData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card">
            <div className="card-content">
              <div className="flex items-center">
                <div className="p-2 bg-primary-100 rounded-lg">
                  <Users className="h-6 w-6 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Total Users</p>
                  <p className="text-2xl font-semibold text-secondary-900">{statsData.total_users}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-content">
              <div className="flex items-center">
                <div className="p-2 bg-success-100 rounded-lg">
                  <UserCheck className="h-6 w-6 text-success-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">With Roles</p>
                  <p className="text-2xl font-semibold text-secondary-900">{statsData.users_with_roles}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-content">
              <div className="flex items-center">
                <div className="p-2 bg-warning-100 rounded-lg">
                  <UserX className="h-6 w-6 text-warning-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Without Roles</p>
                  <p className="text-2xl font-semibold text-secondary-900">{statsData.users_without_roles}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-content">
              <div className="flex items-center">
                <div className="p-2 bg-info-100 rounded-lg">
                  <UserIcon className="h-6 w-6 text-info-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Recent (30d)</p>
                  <p className="text-2xl font-semibold text-secondary-900">{statsData.recent_registrations}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="card">
        <div className="card-content">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-secondary-400" />
                <input
                  type="text"
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Role Filter */}
            <div className="w-full md:w-48">
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="w-full px-3 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Roles</option>
                {rolesData?.roles?.map((role: any) => (
                  <option key={role.name} value={role.name}>
                    {role.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div className="w-full md:w-48">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card">
        <div className="card-content">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-secondary-600">Loading users...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-secondary-200">
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">User</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Roles</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Permissions</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Joined</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {usersData?.users?.map((user: UserWithRoles) => (
                    <tr key={user.id} className="border-b border-secondary-100 hover:bg-secondary-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center">
                          <div className="h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center">
                            <UserIcon className="h-5 w-5 text-primary-600" />
                          </div>
                          <div className="ml-3">
                            <p className="font-medium text-secondary-900">{user.name} {user.surname}</p>
                            <p className="text-sm text-secondary-600">{user.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex flex-wrap gap-1">
                          {user.roles?.map((role) => (
                            <span
                              key={role.id}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                            >
                              {role.name}
                            </span>
                          ))}
                          {(!user.roles || user.roles.length === 0) && (
                            <span className="text-sm text-secondary-500">No roles</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-secondary-600">
                          {user.total_permissions || 0} permissions
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            user.is_active
                              ? 'bg-success-100 text-success-800'
                              : 'bg-warning-100 text-warning-800'
                          }`}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm text-secondary-600">
                          {new Date(user.created_at).toLocaleDateString()}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleViewUser(user)}
                            className="p-1 text-secondary-400 hover:text-secondary-600"
                            title="View Details"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => {
                              setSelectedUser(user);
                              setShowRoleModal(true);
                            }}
                            className="p-1 text-secondary-400 hover:text-secondary-600"
                            title="Manage Roles"
                          >
                            <Shield className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleMessageUser(user)}
                            className="p-1 text-secondary-400 hover:text-secondary-600"
                            title="Send Message"
                          >
                            <MessageSquare className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* User Details Modal */}
      {showUserModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-secondary-900">User Details</h2>
              <button
                onClick={() => setShowUserModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Name</label>
                  <p className="text-secondary-900">{selectedUser.name} {selectedUser.surname}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Email</label>
                  <p className="text-secondary-900">{selectedUser.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Phone</label>
                  <p className="text-secondary-900">{selectedUser.phone}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700">Username</label>
                  <p className="text-secondary-900">{selectedUser.username}</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Roles</label>
                <div className="space-y-2">
                  {selectedUser.roles?.map((role) => (
                    <div key={role.id} className="flex items-center justify-between p-2 bg-secondary-50 rounded">
                      <span className="font-medium">{role.name}</span>
                      <button
                        onClick={() => handleRemoveRole(selectedUser.id, role.name)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                  {(!selectedUser.roles || selectedUser.roles.length === 0) && (
                    <p className="text-secondary-500">No roles assigned</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Permissions</label>
                <div className="flex flex-wrap gap-1">
                  {selectedUser.permissions?.map((permission, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-secondary-100 text-secondary-800"
                    >
                      {permission}
                    </span>
                  ))}
                  {(!selectedUser.permissions || selectedUser.permissions.length === 0) && (
                    <p className="text-secondary-500">No permissions</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Role Assignment Modal */}
      {showRoleModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-secondary-900">Assign Role</h2>
              <button
                onClick={() => setShowRoleModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  User: {selectedUser.name} {selectedUser.surname}
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">Select Role</label>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {rolesData?.roles?.map((role: any) => (
                    <div
                      key={role.name}
                      className="flex items-center justify-between p-3 border border-secondary-200 rounded-lg hover:bg-secondary-50 cursor-pointer"
                      onClick={() => handleAssignRole(selectedUser.id, role.name)}
                    >
                      <div>
                        <p className="font-medium text-secondary-900">{role.name}</p>
                        <p className="text-sm text-secondary-600">{role.description}</p>
                        <p className="text-xs text-secondary-500">{role.permission_count} permissions</p>
                      </div>
                      <Plus className="h-4 w-4 text-secondary-400" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
