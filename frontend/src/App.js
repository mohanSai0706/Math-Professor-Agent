import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Brain, 
  Shield, 
  Database, 
  Search, 
  Send, 
  ThumbsUp, 
  ThumbsDown,
  Activity,
  CheckCircle,
  AlertCircle,
  Clock,
  User,
  MessageSquare,
  Loader
} from 'lucide-react';

const App = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');
  const [healthStatus, setHealthStatus] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);

  // Check health status on load
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const result = await axios.get('/health');
      setHealthStatus(result.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({ status: 'unhealthy', services: {} });
    }
  };

  const handleSubmit = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError('');
    setResponse(null);

    try {
      const result = await axios.post('/ask', {
        question: question.trim(),
        topic: null,
        difficulty_level: null,
        context: null
      });

      setResponse(result.data);
      setShowFeedback(true);
    } catch (error) {
      console.error('Error:', error);
      setError(error.response?.data?.detail || 'An error occurred while processing your question.');
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (rating, isHelpful, feedbackText = '') => {
    if (!response) return;

    try {
      await axios.post('/feedback', {
        response_id: `${Date.now()}`,
        rating,
        feedback_text: feedbackText,
        is_helpful: isHelpful,
        suggested_improvement: feedbackText
      });
      alert('Thank you for your feedback!');
      setShowFeedback(false);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Error submitting feedback. Please try again.');
    }
  };

  const getRouteColor = (route) => {
    switch (route) {
      case 'knowledge_base': return 'text-green-600';
      case 'web_search': return 'text-purple-600';
      case 'hybrid': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getRouteIcon = (route) => {
    switch (route) {
      case 'knowledge_base': return <Database className="w-4 h-4" />;
      case 'web_search': return <Search className="w-4 h-4" />;
      case 'hybrid': return <Activity className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  // Sample questions for testing
  const sampleQuestions = [
    "What is the derivative of x^2?",
    "What is the area of a circle with radius r?",
    "Latest advances in mathematical optimization 2024",
    "Applications of linear algebra in modern AI systems"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Brain className="w-8 h-8" />
              <div>
                <h1 className="text-2xl font-bold">Math Routing Agent</h1>
                <p className="text-blue-200 text-sm">Agentic-RAG Mathematical Professor System</p>
              </div>
            </div>
            
            {/* Status indicators */}
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5" />
                <span className="text-sm">AI Guardrails</span>
              </div>
              <div className="flex items-center space-x-2">
                <Database className="w-5 h-5" />
                <span className="text-sm">Knowledge Base</span>
              </div>
              <div className="flex items-center space-x-2">
                <Search className="w-5 h-5" />
                <span className="text-sm">Web Search/MCP</span>
              </div>
              
              {/* Health status */}
              <div className="flex items-center space-x-2">
                {healthStatus?.status === 'healthy' ? (
                  <CheckCircle className="w-5 h-5 text-green-300" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-300" />
                )}
                <span className="text-sm capitalize">{healthStatus?.status || 'Unknown'}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Architecture Overview */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
            Agentic-RAG Architecture Overview
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <User className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-800">User Question</h3>
              <p className="text-sm text-gray-600">Mathematical question input</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Shield className="w-8 h-8 text-yellow-600" />
              </div>
              <h3 className="font-semibold text-gray-800">Input Guardrails</h3>
              <p className="text-sm text-gray-600">AI Gateway security check</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Activity className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-800">Routing Agent</h3>
              <p className="text-sm text-gray-600">Decision: KB vs Web Search</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Database className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-800">Knowledge Base</h3>
              <p className="text-sm text-gray-600">Vector DB retrieval</p>
            </div>
          </div>

          <div className="flex items-center justify-center mb-6">
            <Activity className="w-6 h-6 text-blue-600" />
            <span className="text-sm text-gray-600 ml-2">Routes to:</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="border-2 border-green-200 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Database className="w-8 h-8 text-green-600" />
                <div className="ml-3">
                  <h3 className="font-semibold text-gray-800">Knowledge Base Route</h3>
                  <p className="text-sm text-gray-600">Vector DB with mathematical datasets</p>
                </div>
              </div>
              <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                Primary Route
              </span>
            </div>

            <div className="border-2 border-purple-200 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Search className="w-8 h-8 text-purple-600" />
                <div className="ml-3">
                  <h3 className="font-semibold text-gray-800">Web Search/MCP Route</h3>
                  <p className="text-sm text-gray-600">External search when KB insufficient</p>
                </div>
              </div>
              <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
                Fallback Route
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                <Shield className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">Output Guardrails</h3>
                <p className="text-sm text-gray-600">Response validation</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">Human-in-Loop</h3>
                <p className="text-sm text-gray-600">Feedback & learning</p>
              </div>
            </div>
          </div>
        </div>

        {/* Sample Questions */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Try These Sample Questions:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {sampleQuestions.map((sample, index) => (
              <button
                key={index}
                onClick={() => setQuestion(sample)}
                className="text-left p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
              >
                <span className="text-sm text-gray-700">{sample}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Question Input */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Ask a Mathematical Question</h2>
          
          <div className="space-y-4">
            <div>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Enter your mathematical question here... (e.g., What is the derivative of x^2 + 3x + 1?)"
                className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none h-32"
                disabled={loading}
              />
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={loading || !question.trim()}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              {loading ? (
                <>
                  <Loader className="animate-spin w-4 h-4" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Ask Question</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <span className="text-red-800 font-medium">Error:</span>
            </div>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        )}

        {/* Response Display */}
        {response && (
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-800">Solution</h2>
              <div className="flex items-center space-x-4">
                <div className={`flex items-center space-x-2 ${getRouteColor(response.route_used)}`}>
                  {getRouteIcon(response.route_used)}
                  <span className="text-sm font-medium capitalize">
                    {response.route_used.replace('_', ' ')} Route
                  </span>
                </div>
                <div className="flex items-center space-x-2 text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">{response.response_time.toFixed(2)}s</span>
                </div>
              </div>
            </div>

            {/* Question */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-800 mb-2">Question:</h3>
              <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">{response.question}</p>
            </div>

            {/* Steps */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-800 mb-3">Step-by-Step Solution:</h3>
              <div className="space-y-3">
                {response.solution.steps.map((step, index) => (
                  <div key={index} className="flex space-x-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-medium text-sm">{index + 1}</span>
                    </div>
                    <div className="flex-1 bg-gray-50 p-4 rounded-lg">
                      <p className="text-gray-700">{step}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Explanation */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-800 mb-2">Explanation:</h3>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-gray-700">{response.solution.explanation}</p>
              </div>
            </div>

            {/* Final Answer */}
            <div className="mb-6">
              <h3 className="font-semibold text-gray-800 mb-2">Final Answer:</h3>
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <p className="text-green-800 font-medium">{response.solution.final_answer}</p>
              </div>
            </div>

            {/* Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
              <div>
                <span className="text-sm text-gray-600">Difficulty:</span>
                <span className="ml-2 text-sm font-medium capitalize">
                  {response.solution.difficulty_assessment}
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-600">Confidence:</span>
                <span className="ml-2 text-sm font-medium">
                  {(response.confidence_score * 100).toFixed(1)}%
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-600">Sources:</span>
                <span className="ml-2 text-sm">{response.sources.length}</span>
              </div>
            </div>

            {/* Sources */}
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-gray-800 mb-2">Sources:</h4>
              <div className="flex flex-wrap gap-2">
                {response.sources.map((source, index) => (
                  <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                    {source}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Feedback Section */}
        {showFeedback && response && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Rate This Response</h2>
            <p className="text-gray-600 mb-6">Your feedback helps improve our mathematical solutions.</p>
            
            <div className="flex space-x-4">
              <button
                onClick={() => submitFeedback(5, true)}
                className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <ThumbsUp className="w-4 h-4" />
                <span>Helpful</span>
              </button>
              
              <button
                onClick={() => submitFeedback(2, false)}
                className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <ThumbsDown className="w-4 h-4" />
                <span>Not Helpful</span>
              </button>
              
              <button
                onClick={() => setShowFeedback(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Skip
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="container mx-auto px-6 text-center">
          <p className="text-gray-400">
            Math Routing Agent - Agentic-RAG Mathematical Professor System
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Powered by GeminiAI, Tavily, and Qdrant • Intelligent Mathematical Solutions
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;