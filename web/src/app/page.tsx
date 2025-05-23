"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { format } from "date-fns";
import ReactMarkdown from "react-markdown";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import {
  PaperAirplaneIcon,
  DocumentTextIcon,
  UserCircleIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/solid";

interface Message {
  type: "user" | "assistant";
  content: string;
  timestamp: Date;
  status: "sending" | "sent" | "error";
}

// Session ID storage key
const SESSION_STORAGE_KEY = "appliance_repair_session_id";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [modelNumber, setModelNumber] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showModelInput, setShowModelInput] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Initialize session ID from storage or create new one
  useEffect(() => {
    const storedSessionId = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = crypto.randomUUID();
      sessionStorage.setItem(SESSION_STORAGE_KEY, newSessionId);
      setSessionId(newSessionId);
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    try {
      setIsLoading(true);
      const userMessage: Message = {
        type: "user",
        content: input,
        timestamp: new Date(),
        status: "sending"
      };
      setMessages((prev) => [...prev, userMessage]);

      const response = await axios.post(`${process.env.API_URL}/api/chat`, {
        message: input,
        model_number: modelNumber || undefined,
        session_id: sessionId,
      });

      // Store the session ID from response
      if (response.data.session_id && response.data.session_id !== sessionId) {
        sessionStorage.setItem(SESSION_STORAGE_KEY, response.data.session_id);
        setSessionId(response.data.session_id);
      }

      setMessages((prev) =>
        prev.map((msg, idx) =>
          idx === prev.length - 1 ? { ...msg, status: "sent" } : msg
        )
      );

      const assistantMessage: Message = {
        type: "assistant",
        content: response.data.response,
        timestamp: new Date(),
        status: "sent"
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setInput("");
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Error sending message:", error.message);
        console.log('API Error Details:', {
          status: error.response?.status,
          data: error.response?.data,
          config: error.config
        });
      } else {
        console.error("Unexpected error:", error);
      }
      
      setMessages((prev) =>
        prev.map((msg, idx) =>
          idx === prev.length - 1 ? { ...msg, status: "error" } : msg
        )
      );

      const errorMessage: Message = {
        type: "assistant",
        content: "Sorry, there was an error processing your request.",
        timestamp: new Date(),
        status: "error"
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-800 dark:to-gray-900">
      {/* Header */}
      <div className="flex-shrink-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">🔧</span>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">
                  Appliance Repair Assistant
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Get expert help with your appliance issues
                </p>
              </div>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => setShowModelInput(!showModelInput)}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title="Model Number"
              >
                <DocumentTextIcon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
              </button>
              <button
                onClick={() => {
                  const newSessionId = crypto.randomUUID();
                  sessionStorage.setItem(SESSION_STORAGE_KEY, newSessionId);
                  setSessionId(newSessionId);
                  setMessages([]);
                  setModelNumber("");
                  setShowModelInput(false);
                }}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title="New Conversation"
              >
                <ArrowPathIcon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
              </button>
            </div>
          </div>
          
          {showModelInput && (
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Model Number (Optional)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g., WF45R6100AW"
                  value={modelNumber}
                  onChange={(e) => setModelNumber(e.target.value)}
                  className="flex-1 px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                />
                <button
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors font-medium"
                  onClick={() => setShowModelInput(false)}
                >
                  Save
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full max-w-4xl mx-auto px-4 py-6">
          <div className="h-full flex flex-col">
            {messages.length === 0 ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center max-w-md">
                  <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <span className="text-white text-2xl">🔧</span>
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Welcome to Appliance Repair Assistant
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Describe your appliance issue and I'll help you troubleshoot and find solutions.
                  </p>
                  <div className="grid grid-cols-1 gap-3 text-sm">
                    <div className="p-3 bg-white/60 dark:bg-gray-800/60 rounded-lg border border-gray-200 dark:border-gray-700">
                      <span className="font-medium text-gray-900 dark:text-gray-100">💡 Example:</span>
                      <span className="text-gray-600 dark:text-gray-400 ml-2">"My washing machine won't drain"</span>
                    </div>
                    <div className="p-3 bg-white/60 dark:bg-gray-800/60 rounded-lg border border-gray-200 dark:border-gray-700">
                      <span className="font-medium text-gray-900 dark:text-gray-100">🔍 Tip:</span>
                      <span className="text-gray-600 dark:text-gray-400 ml-2">Include your model number for better help</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 overflow-y-auto space-y-4 pb-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === "user" ? "justify-end" : "justify-start"} px-2`}
                  >
                    <div className={`flex ${message.type === "user" ? "flex-row-reverse" : "flex-row"} items-start gap-3`}>
                      {message.type === "assistant" ? (
                        <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                          <span className="text-white text-sm font-bold">AI</span>
                        </div>
                      ) : (
                        <div className="w-8 h-8 bg-gradient-to-br from-gray-600 to-gray-700 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                          <UserCircleIcon className="w-5 h-5 text-white" />
                        </div>
                      )}
                      
                      <div
                        className={`chat-bubble ${
                          message.type === "user" 
                            ? "user-message" 
                            : "assistant-message"
                        }`}
                      >
                        {message.type === "assistant" ? (
                          <div className="prose prose-sm max-w-none dark:prose-invert">
                            <ReactMarkdown components={{
                              p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
                              pre: ({children}) => <pre className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-x-auto">{children}</pre>,
                              code: ({children}) => <code className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm">{children}</code>,
                              ul: ({children}) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
                              ol: ({children}) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
                              li: ({children}) => <li className="mb-1">{children}</li>,
                              h1: ({children}) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                              h2: ({children}) => <h2 className="text-base font-bold mb-2">{children}</h2>,
                              h3: ({children}) => <h3 className="text-sm font-bold mb-2">{children}</h3>,
                              h4: ({children}) => <h4 className="text-sm font-semibold mb-2">{children}</h4>,
                            }}>
                              {message.content}
                            </ReactMarkdown>
                          </div>
                        ) : (
                          <p className="text-white">{message.content}</p>
                        )}
                        
                        <div className={`flex items-center justify-between mt-2 text-xs ${
                          message.type === "user" ? "text-blue-200" : "text-gray-500 dark:text-gray-400"
                        }`}>
                          <span>{format(message.timestamp, "HH:mm")}</span>
                          {message.type === "user" && (
                            <span className="flex items-center gap-1">
                              {message.status === "sending" && (
                                <>
                                  <div className="w-2 h-2 bg-blue-300 rounded-full animate-pulse"></div>
                                  Sending...
                                </>
                              )}
                              {message.status === "error" && (
                                <>
                                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                                  Error
                                </>
                              )}
                              {message.status === "sent" && (
                                <>
                                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                  ✓
                                </>
                              )}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start px-2">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                        <span className="text-white text-sm font-bold">AI</span>
                      </div>
                      <div className="assistant-message">
                        <div className="flex items-center gap-2">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                          <span className="text-gray-500 dark:text-gray-400 text-sm">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chat Input */}
      <div className="flex-shrink-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-t border-gray-200/50 dark:border-gray-700/50">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Describe your appliance issue..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
                  className="w-full px-4 py-3 pr-12 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 shadow-sm"
                  disabled={isLoading}
                />
                {modelNumber && (
                  <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
                    <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200">
                      {modelNumber}
                    </span>
                  </div>
                )}
              </div>
            </div>
            <button
              className="p-3 bg-gradient-to-br from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
