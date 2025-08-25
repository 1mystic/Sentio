import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Book, Clock, User, Search, Filter, ArrowLeft, ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";

const educationalMaterials = [
  {
    id: 1,
    title: "Understanding Anxiety: A Comprehensive Guide",
    description: "Learn about anxiety disorders, their symptoms, causes, and effective management strategies.",
    category: "Anxiety",
    readTime: "12 min",
    author: "Dr. Sarah Johnson",
    difficulty: "Beginner",
    tags: ["anxiety", "symptoms", "management"],
    content: `
      Anxiety is a natural response to stress that everyone experiences. However, when anxiety becomes persistent, excessive, or interferes with daily life, it may indicate an anxiety disorder.
      
      ## Common Types of Anxiety Disorders:
      - Generalized Anxiety Disorder (GAD)
      - Panic Disorder
      - Social Anxiety Disorder
      - Specific Phobias
      
      ## Symptoms to Watch For:
      - Persistent worry or fear
      - Physical symptoms (rapid heartbeat, sweating, trembling)
      - Avoidance of certain situations
      - Sleep disturbances
      
      ## Management Strategies:
      - Deep breathing exercises
      - Progressive muscle relaxation
      - Cognitive restructuring
      - Regular exercise
      - Mindfulness and meditation
    `
  },
  {
    id: 2,
    title: "Depression: Recognizing Signs and Seeking Help",
    description: "A detailed overview of depression, its impact, and pathways to recovery.",
    category: "Depression",
    readTime: "15 min",
    author: "Dr. Michael Chen",
    difficulty: "Beginner",
    tags: ["depression", "symptoms", "treatment"],
    content: `
      Depression is more than just feeling sad or going through a rough patch. It's a serious mental health condition that affects how you feel, think, and handle daily activities.
      
      ## Key Signs of Depression:
      - Persistent sad, anxious, or empty mood
      - Loss of interest in activities once enjoyed
      - Fatigue and decreased energy
      - Changes in appetite or weight
      - Sleep disturbances
      - Feelings of worthlessness or guilt
      
      ## Types of Depression:
      - Major Depressive Disorder
      - Persistent Depressive Disorder
      - Seasonal Affective Disorder
      - Postpartum Depression
      
      ## Treatment Options:
      - Therapy (CBT, DBT, IPT)
      - Medication
      - Lifestyle changes
      - Support groups
    `
  },
  {
    id: 3,
    title: "Building Emotional Resilience",
    description: "Develop skills to bounce back from challenges and maintain mental wellness.",
    category: "Resilience",
    readTime: "10 min",
    author: "Dr. Emily Rodriguez",
    difficulty: "Intermediate",
    tags: ["resilience", "coping", "wellness"],
    content: `
      Emotional resilience is the ability to adapt to stressful situations and bounce back from adversity. It's a skill that can be developed and strengthened over time.
      
      ## Key Components of Resilience:
      - Emotional awareness and regulation
      - Problem-solving skills
      - Social connections
      - Self-care practices
      - Optimistic thinking patterns
      
      ## Building Resilience:
      1. Practice mindfulness and self-awareness
      2. Develop healthy coping strategies
      3. Build strong relationships
      4. Set realistic goals
      5. Learn from setbacks
      6. Take care of your physical health
      
      ## Daily Practices:
      - Gratitude journaling
      - Regular exercise
      - Adequate sleep
      - Connecting with loved ones
      - Engaging in hobbies
    `
  },
  {
    id: 4,
    title: "Stress Management Techniques",
    description: "Practical strategies for managing stress in daily life and work environments.",
    category: "Stress",
    readTime: "8 min",
    author: "Dr. James Wilson",
    difficulty: "Beginner",
    tags: ["stress", "management", "workplace"],
    content: `
      Stress is a normal part of life, but chronic stress can have serious effects on both physical and mental health. Learning effective stress management techniques is crucial for overall wellbeing.
      
      ## Types of Stress:
      - Acute stress (short-term)
      - Chronic stress (long-term)
      - Episodic acute stress
      
      ## Physical Signs of Stress:
      - Headaches
      - Muscle tension
      - Fatigue
      - Sleep problems
      - Digestive issues
      
      ## Effective Stress Management:
      - Time management
      - Relaxation techniques
      - Physical exercise
      - Healthy lifestyle choices
      - Social support
      - Professional help when needed
    `
  },
  {
    id: 5,
    title: "Mindfulness and Mental Health",
    description: "Explore how mindfulness practices can improve mental wellbeing and reduce symptoms.",
    category: "Mindfulness",
    readTime: "12 min",
    author: "Dr. Lisa Park",
    difficulty: "Intermediate",
    tags: ["mindfulness", "meditation", "wellness"],
    content: `
      Mindfulness is the practice of purposeful, non-judgmental awareness of the present moment. Research shows it can significantly improve mental health outcomes.
      
      ## Benefits of Mindfulness:
      - Reduced anxiety and depression
      - Improved emotional regulation
      - Better stress management
      - Enhanced focus and concentration
      - Increased self-awareness
      
      ## Mindfulness Techniques:
      - Breathing meditation
      - Body scan exercises
      - Mindful walking
      - Loving-kindness meditation
      - Mindful eating
      
      ## Getting Started:
      1. Start with just 5 minutes daily
      2. Use guided meditations
      3. Practice consistency over perfection
      4. Be patient with yourself
      5. Join a mindfulness group or class
    `
  }
];

const categories = ["All", "Anxiety", "Depression", "Stress", "Resilience", "Mindfulness"];
const difficulties = ["All", "Beginner", "Intermediate", "Advanced"];

const EducationalMaterials = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedDifficulty, setSelectedDifficulty] = useState("All");
  const [selectedMaterial, setSelectedMaterial] = useState<typeof educationalMaterials[0] | null>(null);

  const filteredMaterials = educationalMaterials.filter(material => {
    const matchesSearch = material.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         material.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         material.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === "All" || material.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === "All" || material.difficulty === selectedDifficulty;
    
    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  if (selectedMaterial) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <Button 
              variant="ghost" 
              onClick={() => setSelectedMaterial(null)}
              className="mb-4"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Materials
            </Button>
            
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary">{selectedMaterial.category}</Badge>
              <Badge variant="outline">{selectedMaterial.difficulty}</Badge>
            </div>
            
            <h1 className="text-3xl font-bold text-mind-gray-dark mb-2">
              {selectedMaterial.title}
            </h1>
            
            <div className="flex items-center gap-4 text-sm text-mind-gray mb-4">
              <div className="flex items-center gap-1">
                <User className="h-4 w-4" />
                {selectedMaterial.author}
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {selectedMaterial.readTime}
              </div>
            </div>
            
            <p className="text-lg text-mind-gray mb-6">{selectedMaterial.description}</p>
          </div>
          
          <Card>
            <CardContent className="p-8">
              <div className="prose max-w-none">
                {selectedMaterial.content.split('\n').map((paragraph, index) => {
                  if (paragraph.trim().startsWith('## ')) {
                    return (
                      <h2 key={index} className="text-xl font-semibold mt-6 mb-3 text-mind-gray-dark">
                        {paragraph.replace('## ', '')}
                      </h2>
                    );
                  } else if (paragraph.trim().startsWith('- ')) {
                    return (
                      <li key={index} className="ml-4 mb-1">
                        {paragraph.replace('- ', '')}
                      </li>
                    );
                  } else if (paragraph.trim().match(/^\d+\./)) {
                    return (
                      <li key={index} className="ml-4 mb-1 list-decimal">
                        {paragraph.replace(/^\d+\.\s/, '')}
                      </li>
                    );
                  } else if (paragraph.trim()) {
                    return (
                      <p key={index} className="mb-4 text-mind-gray leading-relaxed">
                        {paragraph.trim()}
                      </p>
                    );
                  }
                  return null;
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="mb-8">
        <Link to="/resources" className="text-mind-blue-dark hover:underline mb-4 inline-block">
          ← Back to Resources
        </Link>
        <h1 className="text-3xl font-bold text-mind-gray-dark">Educational Materials</h1>
        <p className="text-mind-gray mt-1">
          Explore comprehensive guides and articles about mental health topics
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-mind-gray h-4 w-4" />
            <Input
              placeholder="Search materials..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Button variant="outline" className="flex items-center gap-2">
            <Filter className="h-4 w-4" />
            Filters
          </Button>
        </div>

        <div className="flex flex-wrap gap-4">
          <div>
            <label className="text-sm font-medium text-mind-gray-dark mb-2 block">Category</label>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category)}
                >
                  {category}
                </Button>
              ))}
            </div>
          </div>
          
          <div>
            <label className="text-sm font-medium text-mind-gray-dark mb-2 block">Difficulty</label>
            <div className="flex flex-wrap gap-2">
              {difficulties.map((difficulty) => (
                <Button
                  key={difficulty}
                  variant={selectedDifficulty === difficulty ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedDifficulty(difficulty)}
                >
                  {difficulty}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Materials Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredMaterials.map((material) => (
          <Card key={material.id} className="card-hover cursor-pointer" onClick={() => setSelectedMaterial(material)}>
            <CardHeader>
              <div className="flex items-center justify-between mb-2">
                <Badge variant="secondary">{material.category}</Badge>
                <Badge variant="outline">{material.difficulty}</Badge>
              </div>
              <CardTitle className="text-lg">{material.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-mind-gray text-sm mb-4">{material.description}</p>
              
              <div className="flex items-center justify-between text-sm text-mind-gray mb-4">
                <div className="flex items-center gap-1">
                  <User className="h-4 w-4" />
                  {material.author}
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {material.readTime}
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mb-4">
                {material.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>

              <Button variant="outline" className="w-full">
                <Book className="mr-2 h-4 w-4" />
                Read Article
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredMaterials.length === 0 && (
        <div className="text-center py-12">
          <Book className="mx-auto h-12 w-12 text-mind-gray mb-4" />
          <h3 className="text-lg font-medium text-mind-gray-dark mb-2">No materials found</h3>
          <p className="text-mind-gray">Try adjusting your search or filter criteria.</p>
        </div>
      )}
    </DashboardLayout>
  );
};

export default EducationalMaterials;
