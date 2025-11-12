import { useState } from 'react'
import './Chatbot.css'

interface Message {
  role: 'user' | 'bot'
  content: string
  tasks?: ChatTask[]
}

interface ChatTask {
  task_id: number
  task_name: string
  module?: string
  end_date?: string
  completion_percent?: number
  status?: string
}

const API_URL = ''

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'bot',
      content: "Hello! I'm your project monitoring assistant. I can help you query tasks by date, view all tasks, and delete tasks. What would you like to know?"
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/chatbot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      })

      const data = await response.json()
      
      setMessages(prev => [...prev, {
        role: 'bot',
        content: data.response || 'I encountered an error processing your request.',
        tasks: data.tasks || []
      }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'bot',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const deleteTask = async (taskId: number) => {
    if (!window.confirm(`Are you sure you want to delete task ${taskId}?`)) {
      return
    }

    try {
      const response = await fetch(`${API_URL}/api/tasks/${taskId}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      
      if (data.success) {
        setMessages(prev => [...prev, {
          role: 'bot',
          content: `✓ ${data.message}. The WBS has been updated and backed up.`
        }])
      } else {
        setMessages(prev => [...prev, {
          role: 'bot',
          content: `Error: ${data.error}`
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'bot',
        content: 'Sorry, I encountered an error deleting the task.'
      }])
    }
  }

  return (
    <>
      <button 
        className={`chatbot-toggle ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle chatbot"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {isOpen && (
        <div className="chatbot-container">
          <div className="chatbot-header">
            <div className="chatbot-title">
              <span className="chatbot-icon">🤖</span>
              <span>Project Assistant</span>
            </div>
            <button 
              className="chatbot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chatbot"
            >
              ✕
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-content">
                  {msg.content}
                </div>
                {msg.tasks && msg.tasks.length > 0 && (
                  <div className="task-results">
                    {msg.tasks.map((task, taskIdx) => (
                      <div key={taskIdx} className="task-item">
                        <div className="task-info">
                          <div className="task-name">
                            <strong>#{task.task_id}</strong> {task.task_name}
                          </div>
                          <div className="task-details">
                            {task.module && <span className="task-module">{task.module}</span>}
                            {task.completion_percent !== undefined && (
                              <span className="task-completion">{task.completion_percent}% complete</span>
                            )}
                            {task.end_date && (
                              <span className="task-date">Due: {task.end_date}</span>
                            )}
                          </div>
                        </div>
                        <button
                          className="task-delete-btn"
                          onClick={() => deleteTask(task.task_id)}
                          title="Delete task"
                        >
                          🗑️
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="message bot">
                <div className="message-content typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
          </div>

          <div className="chatbot-input">
            <input
              type="text"
              placeholder="Ask me about tasks, dates, or type 'help'..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <button 
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              ➤
            </button>
          </div>

          <div className="chatbot-footer">
            <div className="quick-actions">
              <button onClick={() => setInput('Show me all tasks')} className="quick-btn">
                📋 All Tasks
              </button>
              <button onClick={() => setInput('Show me tasks due before Oct 9')} className="quick-btn">
                📅 By Date
              </button>
              <button onClick={() => setInput('help')} className="quick-btn">
                ❓ Help
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
