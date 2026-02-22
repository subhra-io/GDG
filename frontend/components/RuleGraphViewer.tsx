'use client';

import { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
  BackgroundVariant,
  Panel,
  useReactFlow,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { toPng, toSvg } from 'html-to-image';

interface RuleGraphData {
  nodes: Array<{
    id: string;
    label: string;
    description: string;
    severity: string;
    precedence: number;
    is_active: boolean;
    parent_rule_id: string | null;
    type: string;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    type: string;
    label: string;
    description: string | null;
  }>;
  policy_id: string;
  stats: {
    total_rules: number;
    total_dependencies: number;
    by_severity?: {
      critical: number;
      high: number;
      medium: number;
      low: number;
    };
  };
}

interface Conflict {
  rule1_id: string;
  rule1_description: string;
  rule2_id: string;
  rule2_description: string;
  conflict_type: string;
  description?: string;
}

interface RuleGraphViewerProps {
  policyId: string;
}

const getSeverityColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return '#dc2626'; // red-600
    case 'high':
      return '#ea580c'; // orange-600
    case 'medium':
      return '#ca8a04'; // yellow-600
    case 'low':
      return '#2563eb'; // blue-600
    default:
      return '#6b7280'; // gray-500
  }
};

const getEdgeColor = (type: string): string => {
  switch (type.toLowerCase()) {
    case 'requires':
      return '#2563eb'; // blue
    case 'conflicts':
      return '#dc2626'; // red
    case 'extends':
      return '#16a34a'; // green
    default:
      return '#6b7280'; // gray
  }
};

function RuleGraphViewerInner({ policyId }: RuleGraphViewerProps) {
  const [graphData, setGraphData] = useState<RuleGraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [cycles, setCycles] = useState<string[][]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [showConflicts, setShowConflicts] = useState(false);
  const [showCycles, setShowCycles] = useState(false);
  const [layoutDirection, setLayoutDirection] = useState<'TB' | 'LR'>('TB');
  const reactFlowInstance = useReactFlow();

  useEffect(() => {
    fetchGraphData();
    fetchConflicts();
    fetchCycles();
  }, [policyId]);

  const fetchConflicts = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/rules/conflicts/${policyId}`);
      if (response.ok) {
        const data = await response.json();
        setConflicts(data.conflicts || []);
      }
    } catch (err) {
      console.error('Failed to fetch conflicts:', err);
    }
  };

  const fetchCycles = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/rules/cycles/${policyId}`);
      if (response.ok) {
        const data = await response.json();
        setCycles(data.cycles || []);
      }
    } catch (err) {
      console.error('Failed to fetch cycles:', err);
    }
  };

  const fetchGraphData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/api/v1/rules/graph/${policyId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch rule graph');
      }
      
      const data: RuleGraphData = await response.json();
      setGraphData(data);
      
      // Convert to ReactFlow format with layout
      const flowNodes: Node[] = data.nodes.map((node, index) => {
        const isInConflict = conflicts.some(c => c.rule1_id === node.id || c.rule2_id === node.id);
        const isInCycle = cycles.some(cycle => cycle.includes(node.id));
        
        return {
          id: node.id,
          type: 'default',
          data: {
            label: (
              <div className="px-4 py-2">
                <div className="font-semibold text-sm mb-1">{node.label}</div>
                <div className="text-xs text-gray-600">
                  {node.severity.toUpperCase()} | Precedence: {node.precedence}
                </div>
                {(isInConflict || isInCycle) && (
                  <div className="text-xs mt-1">
                    {isInConflict && <span className="text-red-600">⚠️ Conflict</span>}
                    {isInCycle && <span className="text-orange-600 ml-2">🔄 Cycle</span>}
                  </div>
                )}
              </div>
            ),
            fullData: node,
          },
          position: layoutDirection === 'TB' 
            ? { x: (index % 3) * 300, y: Math.floor(index / 3) * 150 }
            : { x: Math.floor(index / 3) * 300, y: (index % 3) * 150 },
          style: {
            background: '#fff',
            border: `3px solid ${
              isInConflict && showConflicts ? '#dc2626' :
              isInCycle && showCycles ? '#ea580c' :
              getSeverityColor(node.severity)
            }`,
            borderRadius: '8px',
            padding: 0,
            width: 250,
            boxShadow: (isInConflict && showConflicts) || (isInCycle && showCycles) 
              ? '0 0 20px rgba(220, 38, 38, 0.5)' 
              : undefined,
          },
        };
      });
      
      const flowEdges: Edge[] = data.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        type: 'smoothstep',
        animated: edge.type === 'conflicts',
        style: {
          stroke: getEdgeColor(edge.type),
          strokeWidth: 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: getEdgeColor(edge.type),
        },
      }));
      
      setNodes(flowNodes);
      setEdges(flowEdges);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.id === selectedNode ? null : node.id);
  }, [selectedNode]);

  const exportToPng = useCallback(() => {
    const viewport = document.querySelector('.react-flow__viewport') as HTMLElement;
    if (viewport) {
      toPng(viewport, {
        backgroundColor: '#ffffff',
        width: viewport.offsetWidth,
        height: viewport.offsetHeight,
      })
        .then((dataUrl) => {
          const link = document.createElement('a');
          link.download = `rule-graph-${policyId}.png`;
          link.href = dataUrl;
          link.click();
        })
        .catch((err) => {
          console.error('Failed to export PNG:', err);
        });
    }
  }, [policyId]);

  const exportToSvg = useCallback(() => {
    const viewport = document.querySelector('.react-flow__viewport') as HTMLElement;
    if (viewport) {
      toSvg(viewport, {
        backgroundColor: '#ffffff',
        width: viewport.offsetWidth,
        height: viewport.offsetHeight,
      })
        .then((dataUrl) => {
          const link = document.createElement('a');
          link.download = `rule-graph-${policyId}.svg`;
          link.href = dataUrl;
          link.click();
        })
        .catch((err) => {
          console.error('Failed to export SVG:', err);
        });
    }
  }, [policyId]);

  const exportToJson = useCallback(() => {
    if (graphData) {
      const dataStr = JSON.stringify(graphData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.download = `rule-graph-${policyId}.json`;
      link.href = url;
      link.click();
      URL.revokeObjectURL(url);
    }
  }, [graphData, policyId]);

  const autoLayout = useCallback(() => {
    if (reactFlowInstance) {
      reactFlowInstance.fitView({ padding: 0.2, duration: 800 });
    }
  }, [reactFlowInstance]);

  const toggleLayout = useCallback(() => {
    setLayoutDirection(prev => prev === 'TB' ? 'LR' : 'TB');
    // Re-fetch to trigger re-layout
    fetchGraphData();
  }, []);

  const selectedNodeData = selectedNode 
    ? nodes.find(n => n.id === selectedNode)?.data?.fullData 
    : null;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading rule graph...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error Loading Graph</h3>
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchGraphData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-yellow-800 font-semibold mb-2">No Rules Found</h3>
        <p className="text-yellow-700">
          This policy doesn't have any rules yet. Upload a policy document and extract rules to see the graph.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Stats Bar */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{graphData.stats.total_rules}</div>
            <div className="text-sm text-gray-600">Total Rules</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{graphData.stats.total_dependencies}</div>
            <div className="text-sm text-gray-600">Dependencies</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{conflicts.length}</div>
            <div className="text-sm text-gray-600">Conflicts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{cycles.length}</div>
            <div className="text-sm text-gray-600">Cycles</div>
          </div>
          {graphData.stats.by_severity && (
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{graphData.stats.by_severity.critical}</div>
              <div className="text-sm text-gray-600">Critical</div>
            </div>
          )}
        </div>
      </div>

      {/* Control Bar */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setShowConflicts(!showConflicts)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              showConflicts 
                ? 'bg-red-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {showConflicts ? '✓' : ''} Highlight Conflicts ({conflicts.length})
          </button>
          <button
            onClick={() => setShowCycles(!showCycles)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              showCycles 
                ? 'bg-orange-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {showCycles ? '✓' : ''} Highlight Cycles ({cycles.length})
          </button>
          <button
            onClick={toggleLayout}
            className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200"
          >
            Layout: {layoutDirection === 'TB' ? 'Top-Bottom' : 'Left-Right'}
          </button>
          <button
            onClick={autoLayout}
            className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg text-sm font-medium hover:bg-purple-200"
          >
            Auto Fit
          </button>
          <div className="ml-auto flex gap-2">
            <button
              onClick={exportToPng}
              className="px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200"
            >
              Export PNG
            </button>
            <button
              onClick={exportToSvg}
              className="px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200"
            >
              Export SVG
            </button>
            <button
              onClick={exportToJson}
              className="px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200"
            >
              Export JSON
            </button>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-semibold mb-3">Legend</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded border-2 border-red-600"></div>
            <span>Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded border-2 border-orange-600"></div>
            <span>High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded border-2 border-yellow-600"></div>
            <span>Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded border-2 border-blue-600"></div>
            <span>Low</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-blue-600"></div>
            <span>Requires</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-red-600"></div>
            <span>Conflicts</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-green-600"></div>
            <span>Extends</span>
          </div>
        </div>
      </div>

      {/* Graph and Details Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Graph */}
        <div className={`bg-white rounded-lg shadow ${selectedNode ? 'lg:col-span-2' : 'lg:col-span-3'}`} style={{ height: '600px' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
          >
            <Controls />
            <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
          </ReactFlow>
        </div>

        {/* Node Details Panel */}
        {selectedNode && selectedNodeData && (
          <div className="bg-white rounded-lg shadow p-4 overflow-y-auto" style={{ height: '600px' }}>
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Rule Details</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-gray-500 uppercase">Severity</label>
                <div className={`mt-1 px-3 py-1 rounded-full text-sm font-medium inline-block ${
                  selectedNodeData.severity === 'critical' ? 'bg-red-100 text-red-800' :
                  selectedNodeData.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                  selectedNodeData.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {selectedNodeData.severity.toUpperCase()}
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 uppercase">Description</label>
                <p className="mt-1 text-sm text-gray-700">{selectedNodeData.description}</p>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 uppercase">Precedence</label>
                <p className="mt-1 text-sm text-gray-700">{selectedNodeData.precedence}</p>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-500 uppercase">Status</label>
                <p className="mt-1 text-sm text-gray-700">
                  {selectedNodeData.is_active ? '✓ Active' : '✗ Inactive'}
                </p>
              </div>

              {selectedNodeData.parent_rule_id && (
                <div>
                  <label className="text-xs font-semibold text-gray-500 uppercase">Parent Rule</label>
                  <p className="mt-1 text-sm text-gray-700">{selectedNodeData.parent_rule_id}</p>
                </div>
              )}

              {/* Show conflicts involving this rule */}
              {conflicts.filter(c => c.rule1_id === selectedNode || c.rule2_id === selectedNode).length > 0 && (
                <div>
                  <label className="text-xs font-semibold text-red-600 uppercase">⚠️ Conflicts</label>
                  <div className="mt-2 space-y-2">
                    {conflicts
                      .filter(c => c.rule1_id === selectedNode || c.rule2_id === selectedNode)
                      .map((conflict, idx) => (
                        <div key={idx} className="bg-red-50 border border-red-200 rounded p-2 text-xs">
                          <p className="font-medium text-red-800">
                            {conflict.conflict_type === 'explicit' ? 'Explicit Conflict' : 'Potential Conflict'}
                          </p>
                          <p className="text-red-700 mt-1">
                            {conflict.description || 'Rules may have conflicting conditions'}
                          </p>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Show cycles involving this rule */}
              {cycles.filter(cycle => cycle.includes(selectedNode)).length > 0 && (
                <div>
                  <label className="text-xs font-semibold text-orange-600 uppercase">🔄 Circular Dependencies</label>
                  <div className="mt-2 space-y-2">
                    {cycles
                      .filter(cycle => cycle.includes(selectedNode))
                      .map((cycle, idx) => (
                        <div key={idx} className="bg-orange-50 border border-orange-200 rounded p-2 text-xs">
                          <p className="text-orange-700">
                            Cycle detected: {cycle.length} rules involved
                          </p>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">How to Use</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Click on a node to view detailed information</li>
          <li>• Drag nodes to rearrange the graph</li>
          <li>• Scroll to zoom in/out</li>
          <li>• Use "Highlight Conflicts" to see conflicting rules</li>
          <li>• Use "Highlight Cycles" to see circular dependencies</li>
          <li>• Export graph as PNG, SVG, or JSON</li>
          <li>• Toggle layout direction for better visualization</li>
        </ul>
      </div>

      {/* Conflicts List */}
      {showConflicts && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold text-gray-900 mb-3">
            Detected Conflicts {conflicts.length > 0 ? `(${conflicts.length})` : ''}
          </h3>
          {conflicts.length > 0 ? (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {conflicts.map((conflict, idx) => (
                <div key={idx} className="bg-red-50 border border-red-200 rounded p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-red-900">
                        {conflict.conflict_type === 'explicit' ? 'Explicit Conflict' : 'Potential Conflict'}
                      </p>
                      <p className="text-xs text-red-700 mt-1">
                        Rule 1: {conflict.rule1_description.substring(0, 60)}...
                      </p>
                      <p className="text-xs text-red-700">
                        Rule 2: {conflict.rule2_description.substring(0, 60)}...
                      </p>
                      {conflict.description && (
                        <p className="text-xs text-red-600 mt-1 italic">{conflict.description}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-green-50 border border-green-200 rounded p-4">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-green-900">No Rule Conflicts Detected</p>
                  <p className="text-xs text-green-700 mt-1">
                    All rules are compatible with each other. No conflicting conditions found.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Cycles List */}
      {showCycles && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold text-gray-900 mb-3">
            Circular Dependencies {cycles.length > 0 ? `(${cycles.length})` : ''}
          </h3>
          {cycles.length > 0 ? (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {cycles.map((cycle, idx) => (
                <div key={idx} className="bg-orange-50 border border-orange-200 rounded p-3">
                  <p className="text-sm font-medium text-orange-900">
                    Cycle {idx + 1}: {cycle.length} rules involved
                  </p>
                  <p className="text-xs text-orange-700 mt-1">
                    This creates a circular dependency that may cause issues
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-green-50 border border-green-200 rounded p-4">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-green-900">No Circular Dependencies Detected</p>
                  <p className="text-xs text-green-700 mt-1">
                    All rule dependencies form a valid directed acyclic graph (DAG). This is good for system stability.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function RuleGraphViewer(props: RuleGraphViewerProps) {
  return (
    <ReactFlowProvider>
      <RuleGraphViewerInner {...props} />
    </ReactFlowProvider>
  );
}
