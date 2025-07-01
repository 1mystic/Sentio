
import { useParams } from "react-router-dom";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Brain, BookOpen, PenTool, Compass } from "lucide-react";

const ModuleDetail = () => {
  const { moduleId } = useParams();

  // This would typically come from your database
  const moduleData = {
    "anxiety-toolkit": {
      title: "Anxiety Toolkit",
      description: "Learn to understand and manage anxiety effectively",
      icon: Brain,
      progress: 60,
      sections: [
        {
          title: "Understanding Anxiety",
          description: "Learn about what anxiety is and how it affects you",
          status: "completed"
        },
        {
          title: "Identifying Triggers",
          description: "Recognize what triggers your anxiety",
          status: "in-progress"
        },
        {
          title: "Coping Strategies",
          description: "Practical techniques for managing anxiety",
          status: "locked"
        },
        {
          title: "Building Resilience",
          description: "Long-term strategies for anxiety management",
          status: "locked"
        }
      ]
    },
    // Add other modules as needed
  }[moduleId || ""] || null;

  if (!moduleData) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold text-mind-gray-dark mb-2">Module Not Found</h1>
          <p className="text-mind-gray">The module you're looking for doesn't exist.</p>
        </div>
      </DashboardLayout>
    );
  }

  const ModuleIcon = moduleData.icon;

  return (
    <DashboardLayout>
      <header className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <div className="bg-mind-purple-light p-3 rounded-full">
            <ModuleIcon className="text-mind-purple-dark" size={24} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-mind-gray-dark">{moduleData.title}</h1>
            <p className="text-mind-gray">{moduleData.description}</p>
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm text-mind-gray">{moduleData.progress}%</span>
          </div>
          <Progress value={moduleData.progress} className="h-2" />
        </div>
      </header>

      <div className="space-y-4">
        {moduleData.sections.map((section, index) => (
          <Card key={index} className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold mb-1">{section.title}</h3>
                  <p className="text-mind-gray text-sm">{section.description}</p>
                </div>
                <Button
                  variant={section.status === "completed" ? "outline" : "default"}
                  disabled={section.status === "locked"}
                >
                  {section.status === "completed" ? "Review" : 
                   section.status === "in-progress" ? "Continue" : "Start"}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </DashboardLayout>
  );
};

export default ModuleDetail;
