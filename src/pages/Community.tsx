
import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  Send,
  MessageCircle,
  Users,
  Flag
} from "lucide-react";

type Message = {
  id: number;
  user: {
    name: string;
    avatar?: string;
    initials: string;
  };
  content: string;
  timestamp: string;
  likes: number;
  dislikes: number;
  replies: number;
  biasChecked: boolean;
  biasResult?: string;
};

type Thread = {
  id: number;
  title: string;
  author: {
    name: string;
    avatar?: string;
    initials: string;
  };
  timestamp: string;
  messageCount: number;
  lastActivity: string;
  tags: string[];
};

const Community = () => {
  const [messageInput, setMessageInput] = useState("");
  const [selectedThread, setSelectedThread] = useState<Thread | null>(null);

  // Sample messages data
  const messages: Message[] = [
    {
      id: 1,
      user: {
        name: "Alex Johnson",
        initials: "AJ"
      },
      content: "I've been struggling with perfectionism lately. Anyone else experience this and have tips for overcoming it?",
      timestamp: "Today at 10:32 AM",
      likes: 5,
      dislikes: 0,
      replies: 3,
      biasChecked: true,
      biasResult: "Possible all-or-nothing thinking detected"
    },
    {
      id: 2,
      user: {
        name: "Jamie Smith",
        initials: "JS"
      },
      content: "I've found that mindfulness meditation has really helped me with anxiety. Have any of you tried it?",
      timestamp: "Today at 9:45 AM",
      likes: 8,
      dislikes: 1,
      replies: 4,
      biasChecked: false
    },
    {
      id: 3,
      user: {
        name: "Pat Wilson",
        avatar: "",
        initials: "PW"
      },
      content: "Does anyone else feel like everyone else has their life together except for you? I know it's probably not true but I can't shake the feeling.",
      timestamp: "Yesterday at 2:15 PM",
      likes: 12,
      dislikes: 0,
      replies: 7,
      biasChecked: true,
      biasResult: "Social comparison bias detected"
    }
  ];

  // Sample threads data
  const threads: Thread[] = [
    {
      id: 1,
      title: "Dealing with anxiety at work",
      author: {
        name: "Alex Johnson",
        initials: "AJ"
      },
      timestamp: "April 24, 2025",
      messageCount: 12,
      lastActivity: "2 hours ago",
      tags: ["Anxiety", "Work-Life"]
    },
    {
      id: 2,
      title: "Cognitive bias in everyday decisions",
      author: {
        name: "Jamie Smith",
        initials: "JS"
      },
      timestamp: "April 23, 2025",
      messageCount: 8,
      lastActivity: "Yesterday",
      tags: ["Cognitive Bias", "Decision Making"]
    },
    {
      id: 3,
      title: "Value-based career choices",
      author: {
        name: "Pat Wilson",
        initials: "PW"
      },
      timestamp: "April 21, 2025",
      messageCount: 15,
      lastActivity: "3 days ago",
      tags: ["Career", "Values"]
    }
  ];

  const handleCheckBias = (messageId: number) => {
    console.log(`Checking bias for message ${messageId}`);
    // In a real app, this would send the message to be analyzed
    alert("Bias check initiated. Results will appear shortly.");
  };

  const handleSendMessage = () => {
    if (messageInput.trim()) {
      console.log("Message sent:", messageInput);
      // In a real app, this would add the message to the database
      setMessageInput("");
    }
  };

  return (
    <DashboardLayout>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-mind-gray-dark">Community</h1>
        <p className="text-mind-gray mt-1">
          Connect with others on their mental wellness journey
        </p>
      </header>

      <div className="disclaimer mb-6 flex items-start gap-3">
        <AlertTriangle size={20} />
        <div>
          <strong>Community Guidelines:</strong> Be respectful and supportive. This is not a crisis support forum.
          If you or someone you know needs immediate help, please visit our
          <a href="/resources/crisis" className="text-mind-purple-dark hover:underline ml-1">
            Crisis Resources
          </a> page.
        </div>
      </div>

      <Tabs defaultValue="feed">
        <TabsList className="mb-6">
          <TabsTrigger value="feed">Discussion Feed</TabsTrigger>
          <TabsTrigger value="threads">Topic Threads</TabsTrigger>
        </TabsList>

        <TabsContent value="feed">
          <div className="space-y-6 mb-6">
            {messages.map((message) => (
              <Card key={message.id} className="card-hover">
                <CardContent className="p-6">
                  <div className="flex gap-4">
                    <Avatar>
                      <AvatarImage src={message.user.avatar} />
                      <AvatarFallback className="bg-mind-purple text-white">
                        {message.user.initials}
                      </AvatarFallback>
                    </Avatar>

                    <div className="flex-grow">
                      <div className="flex items-center justify-between">
                        <div className="font-medium">{message.user.name}</div>
                        <div className="text-xs text-mind-gray">{message.timestamp}</div>
                      </div>

                      <div className="mt-2 text-mind-gray-dark">{message.content}</div>

                      {message.biasChecked && message.biasResult && (
                        <div className="mt-2 text-sm bg-mind-blue-light text-mind-blue-dark p-2 rounded-md">
                          <strong>Bias Check Result:</strong> {message.biasResult}
                        </div>
                      )}

                      <div className="flex items-center gap-4 mt-4">
                        <Button variant="ghost" size="sm" className="flex items-center gap-1 text-mind-gray">
                          <ThumbsUp size={16} />
                          <span>{message.likes}</span>
                        </Button>

                        <Button variant="ghost" size="sm" className="flex items-center gap-1 text-mind-gray">
                          <ThumbsDown size={16} />
                          <span>{message.dislikes}</span>
                        </Button>

                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="flex items-center gap-1 text-mind-gray"
                          onClick={() => handleCheckBias(message.id)}
                        >
                          <AlertTriangle size={16} />
                          <span>Check Bias</span>
                        </Button>

                        <Button variant="ghost" size="sm" className="flex items-center gap-1 text-mind-gray">
                          <MessageCircle size={16} />
                          <span>Reply{message.replies > 0 ? ` (${message.replies})` : ""}</span>
                        </Button>

                        <Button variant="ghost" size="sm" className="flex items-center gap-1 text-mind-gray ml-auto">
                          <Flag size={16} />
                          <span>Report</span>
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardContent className="p-6">
              <div className="flex gap-4">
                <Avatar>
                  <AvatarFallback className="bg-mind-purple text-white">ME</AvatarFallback>
                </Avatar>

                <div className="flex-grow">
                  <Input
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    placeholder="Share your thoughts or questions with the community..."
                    className="mb-2"
                  />
                  <div className="flex justify-between">
                    <div className="text-xs text-mind-gray">
                      Please follow our <a href="/community/guidelines" className="text-mind-purple-dark hover:underline">community guidelines</a>.
                    </div>
                    <Button 
                      onClick={handleSendMessage} 
                      disabled={!messageInput.trim()} 
                      className="bg-mind-purple-dark hover:bg-mind-purple-dark/90"
                    >
                      <Send size={16} className="mr-2" />
                      Post
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="threads">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {threads.map((thread) => (
              <Card key={thread.id} className="card-hover cursor-pointer" onClick={() => setSelectedThread(thread)}>
                <CardContent className="p-6">
                  <div>
                    <h3 className="font-semibold mb-1 text-mind-gray-dark">{thread.title}</h3>
                    <div className="flex items-center text-sm text-mind-gray mb-3">
                      <Avatar className="h-6 w-6 mr-2">
                        <AvatarFallback className="bg-mind-purple text-white text-xs">
                          {thread.author.initials}
                        </AvatarFallback>
                      </Avatar>
                      <span>Started by {thread.author.name} on {thread.timestamp}</span>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {thread.tags.map((tag) => (
                        <span 
                          key={tag} 
                          className="px-2 py-1 bg-mind-purple-light text-mind-purple-dark text-xs rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>

                    <div className="flex justify-between text-sm text-mind-gray">
                      <div className="flex items-center">
                        <MessageCircle size={14} className="mr-1" />
                        <span>{thread.messageCount} messages</span>
                      </div>
                      <div>Last activity: {thread.lastActivity}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-6 flex justify-center">
            <Button className="bg-mind-purple hover:bg-mind-purple-dark">
              <Users size={16} className="mr-2" />
              Start New Thread
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
};

export default Community;
