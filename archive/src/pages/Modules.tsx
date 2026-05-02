
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, BookOpen, PenTool, Compass } from "lucide-react";
import { Link } from "react-router-dom";

const Modules = () => {
  const modules = [
    {
      title: "Anxiety Toolkit",
      description: "Understanding and managing anxiety effectively",
      icon: Brain,
      progress: 60,
      slug: "anxiety-toolkit"
    },
    {
      title: "Cognitive Bias Awareness",
      description: "Identify and understand thinking patterns",
      icon: BookOpen,
      progress: 30,
      slug: "cognitive-bias"
    },
    {
      title: "Career Path Explorer",
      description: "Clarify your values and career direction",
      icon: Compass,
      progress: 0,
      slug: "career-path"
    },
    {
      title: "Self-Compassion Builder",
      description: "Develop a kinder relationship with yourself",
      icon: PenTool,
      progress: 0,
      slug: "self-compassion"
    }
  ];

  return (
    <DashboardLayout>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-mind-gray-dark">Learning Modules</h1>
        <p className="text-mind-gray mt-1">
          Explore guided content to deepen your understanding and develop new skills
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {modules.map((module) => (
          <Card key={module.slug} className="card-hover">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="bg-mind-purple-light p-3 rounded-full">
                  <module.icon className="text-mind-purple-dark" size={24} />
                </div>
                <div className="flex-grow">
                  <h3 className="font-semibold mb-1">{module.title}</h3>
                  <p className="text-mind-gray text-sm mb-4">{module.description}</p>
                  <Link to={`/modules/${module.slug}`}>
                    <Button className="w-full bg-mind-purple-dark hover:bg-mind-purple-dark/90">
                      {module.progress > 0 ? "Continue" : "Start"}
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </DashboardLayout>
  );
};

export default Modules;
