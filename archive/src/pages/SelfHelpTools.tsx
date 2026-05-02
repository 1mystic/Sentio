import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { 
  Heart, 
  Brain, 
  Target, 
  Clock, 
  CheckCircle, 
  ArrowLeft, 
  Play, 
  Pause, 
  RotateCcw,
  Download,
  Share2,
  BookOpen
} from "lucide-react";
import { Link } from "react-router-dom";
import { useState, useEffect } from "react";

const selfHelpTools = [
  {
    id: 1,
    title: "Breathing Exercises",
    description: "Guided breathing techniques to reduce anxiety and promote relaxation",
    category: "Relaxation",
    duration: "5-15 min",
    difficulty: "Beginner",
    tools: ["4-7-8 Breathing", "Box Breathing", "Progressive Relaxation"],
    icon: Heart,
    color: "bg-blue-100 text-blue-700"
  },
  {
    id: 2,
    title: "Thought Challenging",
    description: "Cognitive exercises to identify and reframe negative thought patterns",
    category: "Cognitive",
    duration: "10-20 min",
    difficulty: "Intermediate",
    tools: ["Thought Record", "Evidence Examination", "Alternative Perspectives"],
    icon: Brain,
    color: "bg-purple-100 text-purple-700"
  },
  {
    id: 3,
    title: "Mindfulness Meditation",
    description: "Guided meditation practices for present-moment awareness",
    category: "Mindfulness",
    duration: "10-30 min",
    difficulty: "Beginner",
    tools: ["Body Scan", "Loving Kindness", "Mindful Breathing"],
    icon: Target,
    color: "bg-green-100 text-green-700"
  },
  {
    id: 4,
    title: "Mood Tracking",
    description: "Tools to monitor and understand your emotional patterns",
    category: "Assessment",
    duration: "5 min daily",
    difficulty: "Beginner",
    tools: ["Daily Mood Log", "Trigger Identification", "Pattern Analysis"],
    icon: BookOpen,
    color: "bg-orange-100 text-orange-700"
  }
];

// Breathing Exercise Component
const BreathingExercise = () => {
  const [isActive, setIsActive] = useState(false);
  const [currentPhase, setCurrentPhase] = useState("inhale");
  const [seconds, setSeconds] = useState(0);
  const [cycle, setCycle] = useState(0);
  const [exerciseType, setExerciseType] = useState("4-7-8");

  const exercises = {
    "4-7-8": { inhale: 4, hold: 7, exhale: 8 },
    "box": { inhale: 4, hold: 4, exhale: 4, pause: 4 },
    "simple": { inhale: 4, exhale: 4 }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    
    if (isActive) {
      interval = setInterval(() => {
        setSeconds(seconds => seconds + 1);
      }, 1000);
    } else if (!isActive && seconds !== 0) {
      if (interval) clearInterval(interval);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, seconds]);

  const reset = () => {
    setSeconds(0);
    setIsActive(false);
    setCurrentPhase("inhale");
    setCycle(0);
  };

  return (
    <div className="max-w-2xl mx-auto text-center">
      <div className="mb-6">
        <Label htmlFor="exercise-type">Exercise Type</Label>
        <div className="flex gap-2 mt-2">
          {Object.keys(exercises).map((type) => (
            <Button
              key={type}
              variant={exerciseType === type ? "default" : "outline"}
              onClick={() => setExerciseType(type)}
              disabled={isActive}
            >
              {type === "4-7-8" ? "4-7-8 Breathing" : type === "box" ? "Box Breathing" : "Simple Breathing"}
            </Button>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-full w-64 h-64 mx-auto mb-8 flex items-center justify-center relative">
        <div className="text-6xl font-light text-mind-blue-dark">
          {Math.floor(seconds / 60)}:{(seconds % 60).toString().padStart(2, '0')}
        </div>
        <div className="absolute bottom-8 text-lg font-medium text-mind-purple-dark capitalize">
          {currentPhase}
        </div>
      </div>

      <div className="flex justify-center gap-4 mb-6">
        <Button onClick={() => setIsActive(!isActive)} size="lg">
          {isActive ? <Pause className="mr-2 h-5 w-5" /> : <Play className="mr-2 h-5 w-5" />}
          {isActive ? 'Pause' : 'Start'}
        </Button>
        <Button onClick={reset} variant="outline" size="lg">
          <RotateCcw className="mr-2 h-5 w-5" />
          Reset
        </Button>
      </div>

      <div className="text-center">
        <p className="text-mind-gray mb-2">Cycle: {cycle}</p>
        <p className="text-sm text-mind-gray">
          Find a comfortable position and follow the breathing pattern. Focus on your breath and let go of other thoughts.
        </p>
      </div>
    </div>
  );
};

// Thought Record Component
const ThoughtRecord = () => {
  const [situation, setSituation] = useState("");
  const [emotion, setEmotion] = useState("");
  const [intensity, setIntensity] = useState([5]);
  const [automaticThought, setAutomaticThought] = useState("");
  const [evidence, setEvidence] = useState("");
  const [alternativeThought, setAlternativeThought] = useState("");
  const [newIntensity, setNewIntensity] = useState([5]);

  const handleSave = () => {
    const record = {
      situation,
      emotion,
      intensity: intensity[0],
      automaticThought,
      evidence,
      alternativeThought,
      newIntensity: newIntensity[0],
      date: new Date().toISOString()
    };
    
    // In a real app, this would save to a database
    console.log("Thought record saved:", record);
    
    // Reset form
    setSituation("");
    setEmotion("");
    setIntensity([5]);
    setAutomaticThought("");
    setEvidence("");
    setAlternativeThought("");
    setNewIntensity([5]);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Situation</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="Describe the situation that triggered your emotion..."
              value={situation}
              onChange={(e) => setSituation(e.target.value)}
              className="min-h-[100px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Emotion & Intensity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Input
                placeholder="What emotion did you feel? (e.g., anxious, sad, angry)"
                value={emotion}
                onChange={(e) => setEmotion(e.target.value)}
              />
              <div>
                <Label>Intensity (1-10): {intensity[0]}</Label>
                <Slider
                  value={intensity}
                  onValueChange={setIntensity}
                  max={10}
                  min={1}
                  step={1}
                  className="mt-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Automatic Thought</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="What went through your mind? What were you telling yourself?"
              value={automaticThought}
              onChange={(e) => setAutomaticThought(e.target.value)}
              className="min-h-[100px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Evidence</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="What evidence supports or contradicts this thought?"
              value={evidence}
              onChange={(e) => setEvidence(e.target.value)}
              className="min-h-[100px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alternative Thought</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              placeholder="What's a more balanced or realistic way to think about this?"
              value={alternativeThought}
              onChange={(e) => setAlternativeThought(e.target.value)}
              className="min-h-[100px]"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>New Emotion Intensity</CardTitle>
          </CardHeader>
          <CardContent>
            <div>
              <Label>New Intensity (1-10): {newIntensity[0]}</Label>
              <Slider
                value={newIntensity}
                onValueChange={setNewIntensity}
                max={10}
                min={1}
                step={1}
                className="mt-2"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-center gap-4">
        <Button onClick={handleSave} size="lg">
          <Download className="mr-2 h-4 w-4" />
          Save Record
        </Button>
        <Button variant="outline" size="lg">
          <Share2 className="mr-2 h-4 w-4" />
          Share with Therapist
        </Button>
      </div>
    </div>
  );
};

// Mood Tracker Component
const MoodTracker = () => {
  const [currentMood, setCurrentMood] = useState(5);
  const [notes, setNotes] = useState("");
  const [triggers, setTriggers] = useState("");

  const moods = [
    { value: 1, label: "Very Low", emoji: "😢", color: "bg-red-500" },
    { value: 2, label: "Low", emoji: "😔", color: "bg-orange-500" },
    { value: 3, label: "Neutral", emoji: "😐", color: "bg-yellow-500" },
    { value: 4, label: "Good", emoji: "🙂", color: "bg-lime-500" },
    { value: 5, label: "Great", emoji: "😊", color: "bg-green-500" }
  ];

  const handleLogMood = () => {
    const moodEntry = {
      mood: currentMood,
      notes,
      triggers,
      date: new Date().toISOString()
    };
    
    console.log("Mood logged:", moodEntry);
    setNotes("");
    setTriggers("");
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>How are you feeling today?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex justify-between items-center">
            {moods.map((mood) => (
              <div
                key={mood.value}
                className={`flex flex-col items-center p-4 rounded-lg cursor-pointer transition-all ${
                  currentMood === mood.value 
                    ? 'bg-mind-blue-light border-2 border-mind-blue-dark' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setCurrentMood(mood.value)}
              >
                <div className="text-2xl mb-2">{mood.emoji}</div>
                <div className="text-sm font-medium">{mood.label}</div>
              </div>
            ))}
          </div>

          <div className="space-y-4">
            <div>
              <Label htmlFor="notes">Notes (optional)</Label>
              <Textarea
                id="notes"
                placeholder="What's contributing to your mood today?"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="triggers">Triggers or Events</Label>
              <Input
                id="triggers"
                placeholder="Any specific events or situations?"
                value={triggers}
                onChange={(e) => setTriggers(e.target.value)}
                className="mt-1"
              />
            </div>
          </div>

          <Button onClick={handleLogMood} className="w-full">
            Log Today's Mood
          </Button>
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Weekly Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-mind-gray">
            <p>Your mood tracking history will appear here.</p>
            <p className="text-sm mt-2">Start logging your mood daily to see patterns and trends.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const SelfHelpTools = () => {
  const [selectedTool, setSelectedTool] = useState<typeof selfHelpTools[0] | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  if (selectedTool) {
    return (
      <DashboardLayout>
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={() => setSelectedTool(null)}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Tools
          </Button>
          
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="secondary">{selectedTool.category}</Badge>
            <Badge variant="outline">{selectedTool.difficulty}</Badge>
          </div>
          
          <h1 className="text-3xl font-bold text-mind-gray-dark mb-2">
            {selectedTool.title}
          </h1>
          
          <div className="flex items-center gap-4 text-sm text-mind-gray mb-4">
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {selectedTool.duration}
            </div>
          </div>
          
          <p className="text-lg text-mind-gray mb-6">{selectedTool.description}</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="practice">Practice</TabsTrigger>
            <TabsTrigger value="progress">Progress</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>About this tool</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-mind-gray mb-4">{selectedTool.description}</p>
                
                <h4 className="font-semibold mb-2">Available exercises:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {selectedTool.tools.map((tool, index) => (
                    <li key={index} className="text-mind-gray">{tool}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="practice" className="mt-6">
            {selectedTool.id === 1 && <BreathingExercise />}
            {selectedTool.id === 2 && <ThoughtRecord />}
            {selectedTool.id === 4 && <MoodTracker />}
            {selectedTool.id === 3 && (
              <div className="text-center py-12">
                <Target className="mx-auto h-12 w-12 text-mind-gray mb-4" />
                <h3 className="text-lg font-medium text-mind-gray-dark mb-2">Mindfulness Meditation</h3>
                <p className="text-mind-gray mb-4">Guided meditation sessions coming soon.</p>
                <Button variant="outline">Request Early Access</Button>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="progress" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Your Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Sessions completed</span>
                      <span>0/30</span>
                    </div>
                    <Progress value={0} />
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>Current streak</span>
                      <span>0 days</span>
                    </div>
                    <Progress value={0} />
                  </div>
                </div>
                
                <p className="text-mind-gray text-sm mt-4">
                  Start practicing to track your progress and build healthy habits.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="mb-8">
        <Link to="/resources" className="text-mind-blue-dark hover:underline mb-4 inline-block">
          ← Back to Resources
        </Link>
        <h1 className="text-3xl font-bold text-mind-gray-dark">Self-Help Tools</h1>
        <p className="text-mind-gray mt-1">
          Interactive tools and exercises to support your mental wellness journey
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {selfHelpTools.map((tool) => {
          const IconComponent = tool.icon;
          return (
            <Card key={tool.id} className="card-hover cursor-pointer" onClick={() => setSelectedTool(tool)}>
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <div className={`p-3 rounded-full ${tool.color}`}>
                    <IconComponent className="h-6 w-6" />
                  </div>
                  <Badge variant="outline">{tool.difficulty}</Badge>
                </div>
                <CardTitle className="text-lg">{tool.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-mind-gray text-sm mb-4">{tool.description}</p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-mind-gray">Duration:</span>
                    <span className="font-medium">{tool.duration}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-mind-gray">Category:</span>
                    <Badge variant="secondary" className="text-xs">{tool.category}</Badge>
                  </div>
                </div>

                <Button variant="outline" className="w-full">
                  <Play className="mr-2 h-4 w-4" />
                  Start Tool
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <Card className="mt-8 bg-gradient-to-r from-mind-blue-light to-mind-purple-light">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-mind-gray-dark mb-2">Need immediate support?</h3>
          <p className="text-mind-gray mb-4">
            Access quick coping tools and crisis resources when you need them most.
          </p>
          <div className="flex gap-4">
            <Button variant="outline" className="bg-white">
              <Heart className="mr-2 h-4 w-4" />
              Quick Breathing
            </Button>
            <Link to="/resources/find-help">
              <Button variant="outline" className="bg-white">
                <Target className="mr-2 h-4 w-4" />
                Find Help Now
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
};

export default SelfHelpTools;
