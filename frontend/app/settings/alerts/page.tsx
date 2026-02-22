'use client';

import { useState, useEffect } from 'react';
import { Bell, Plus, Edit, Trash2, Power, Mail, MessageSquare, Smartphone } from 'lucide-react';

interface AlertRule {
  id: string;
  name: string;
  description: string;
  trigger_condition: any;
  notification_channels: string[];
  recipients: any;
  is_active: boolean;
  created_at: string;
}

export default function AlertRulesPage() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/alerts/rules');
      const data = await response.json();
      setRules(data.rules || []);
    } catch (error) {
      console.error('Error fetching alert rules:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleActive = async (ruleId: string, currentStatus: boolean) => {
    try {
      await fetch(`http://localhost:8000/api/v1/alerts/rules/${ruleId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !currentStatus })
      });
      
      fetchRules();
    } catch (error) {
      console.error('Error toggling rule:', error);
    }
  };

  const deleteRule = async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this alert rule?')) return;
    
    try {
      await fetch(`http://localhost:8000/api/v1/alerts/rules/${ruleId}`, {
        method: 'DELETE'
      });
      
      fetchRules();
    } catch (error) {
      console.error('Error deleting rule:', error);
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email':
        return <Mail className="w-4 h-4" />;
      case 'slack':
        return <MessageSquare className="w-4 h-4" />;
      case 'in_app':
        return <Smartphone className="w-4 h-4" />;
      default:
        return <Bell className="w-4 h-4" />;
    }
  };

  const formatCondition = (condition: any) => {
    const parts = [];
    if (condition.severity) parts.push(`Severity: ${condition.severity}`);
    if (condition.risk_score_min) parts.push(`Risk Score ≥ ${condition.risk_score_min}`);
    if (condition.risk_score_max) parts.push(`Risk Score ≤ ${condition.risk_score_max}`);
    return parts.join(', ') || 'All violations';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Bell className="w-8 h-8" />
                Alert Rules
              </h1>
              <p className="mt-2 text-gray-600">
                Configure when and how you receive notifications
              </p>
            </div>
            
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
              onClick={() => alert('Create rule functionality coming soon!')}
            >
              <Plus className="w-5 h-5" />
              New Rule
            </button>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Rules</div>
            <div className="text-2xl font-bold text-gray-900">{rules.length}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Active Rules</div>
            <div className="text-2xl font-bold text-green-600">
              {rules.filter(r => r.is_active).length}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Inactive Rules</div>
            <div className="text-2xl font-bold text-gray-400">
              {rules.filter(r => !r.is_active).length}
            </div>
          </div>
        </div>

        {/* Rules List */}
        <div className="space-y-4">
          {loading ? (
            <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
              Loading alert rules...
            </div>
          ) : rules.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
              <Bell className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">No alert rules configured</p>
              <p className="text-sm mt-2">Create your first rule to start receiving notifications</p>
            </div>
          ) : (
            rules.map((rule) => (
              <div
                key={rule.id}
                className={`bg-white rounded-lg shadow p-6 ${
                  !rule.is_active ? 'opacity-60' : ''
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {rule.name}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        rule.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {rule.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    
                    {rule.description && (
                      <p className="text-gray-600 mb-4">{rule.description}</p>
                    )}
                    
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium text-gray-700">Trigger:</span>
                        <span className="text-gray-600">
                          {formatCondition(rule.trigger_condition)}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium text-gray-700">Channels:</span>
                        <div className="flex items-center gap-2">
                          {rule.notification_channels.map((channel) => (
                            <span
                              key={channel}
                              className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded"
                            >
                              {getChannelIcon(channel)}
                              {channel.replace('_', ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium text-gray-700">Recipients:</span>
                        <span className="text-gray-600">
                          {rule.recipients.emails?.length || 0} email(s),{' '}
                          {rule.recipients.user_ids?.length || 0} user(s)
                          {rule.recipients.slack_channels?.length > 0 && 
                            `, ${rule.recipients.slack_channels.length} Slack channel(s)`
                          }
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => toggleActive(rule.id, rule.is_active)}
                      className={`p-2 rounded-lg ${
                        rule.is_active
                          ? 'bg-green-100 text-green-700 hover:bg-green-200'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                      title={rule.is_active ? 'Deactivate' : 'Activate'}
                    >
                      <Power className="w-5 h-5" />
                    </button>
                    
                    <button
                      onClick={() => alert('Edit functionality coming soon!')}
                      className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
                      title="Edit"
                    >
                      <Edit className="w-5 h-5" />
                    </button>
                    
                    <button
                      onClick={() => deleteRule(rule.id)}
                      className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                      title="Delete"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Help Text */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">About Alert Rules</h4>
          <p className="text-sm text-blue-800">
            Alert rules automatically send notifications when violations match specific conditions.
            You can configure multiple channels (email, Slack, in-app) and customize recipients for each rule.
          </p>
        </div>
      </div>
    </div>
  );
}
