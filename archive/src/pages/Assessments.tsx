
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { Clock, Award } from "lucide-react";

const Assessments = () => {
  const availableAssessments = [
    {
      id: "anxiety",
      title: "GAD-7 Anxiety Screening",
      description: "A brief screening tool for generalized anxiety disorder",
      estimatedTime: "2-3 minutes",
      category: "Mental Health",
      status: "Not Started"
    },
    {
      id: "mood",
      title: "PHQ-9 Mood Check",
      description: "A depression screening and symptom rating scale",
      estimatedTime: "3-4 minutes",
      category: "Mental Health",
      status: "Not Started"
    },
    {
      id: "biases",
      title: "Cognitive Bias Inventory",
      description: "Identify common thinking patterns that may affect your decisions",
      estimatedTime: "5-7 minutes",
      category: "Cognitive Patterns",
      status: "Not Started"
    },
    {
      id: "values",
      title: "Core Values Assessment",
      description: "Discover what matters most to you for career and life decisions",
      estimatedTime: "10-12 minutes",
      category: "Self-Discovery",
      status: "Not Started"
    }
  ];
  
  const completedAssessments = [
    {
      id: "stress",
      title: "Perceived Stress Scale",
      description: "Measure your perception of stress in your life",
      completedDate: "April 20, 2025",
      category: "Mental Health"
    }
  ];
  
  return (
    <DashboardLayout>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-mind-gray-dark">Assessments</h1>
        <p className="text-mind-gray mt-1">
          Gain insights about yourself through these evidence-based assessments
        </p>
      </header>
      
      <div className="disclaimer mb-6">
        <strong>Important:</strong> These assessments are for self-awareness and educational purposes only.
        They are not diagnostic tools and do not replace professional evaluation or treatment.
      </div>
      
      <Tabs defaultValue="available" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="available">Available Assessments</TabsTrigger>
          <TabsTrigger value="completed">Completed Assessments</TabsTrigger>
        </TabsList>
        
        <TabsContent value="available">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {availableAssessments.map((assessment) => (
              <Card key={assessment.id} className="card-hover">
                <CardContent className="p-6">
                  <div className="flex flex-col h-full">
                    <div>
                      <Badge variant="outline" className="mb-2 bg-mind-gray-light">
                        {assessment.category}
                      </Badge>
                      <h3 className="text-lg font-semibold mb-2">{assessment.title}</h3>
                      <p className="text-mind-gray text-sm mb-4">{assessment.description}</p>
                    </div>
                    
                    <div className="flex items-center text-sm text-mind-gray mb-6">
                      <Clock size={16} className="mr-1" />
                      <span>{assessment.estimatedTime}</span>
                    </div>
                    
                    <div className="mt-auto">
                      <Link to={`/assessments/${assessment.id}`}>
                        <Button className="w-full bg-mind-purple-dark hover:bg-mind-purple-dark/90">Start Assessment</Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        
        <TabsContent value="completed">
          {completedAssessments.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {completedAssessments.map((assessment) => (
                <Card key={assessment.id} className="card-hover">
                  <CardContent className="p-6">
                    <div className="flex flex-col h-full">
                      <div>
                        <Badge variant="outline" className="mb-2 bg-mind-gray-light">
                          {assessment.category}
                        </Badge>
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-semibold mb-2">{assessment.title}</h3>
                          <Award size={18} className="text-green-600" />
                        </div>
                        <p className="text-mind-gray text-sm mb-4">{assessment.description}</p>
                      </div>
                      
                      <div className="flex items-center text-sm text-mind-gray mb-6">
                        <span>Completed on {assessment.completedDate}</span>
                      </div>
                      
                      <div className="mt-auto flex gap-2">
                        <Link to={`/insights#${assessment.id}`} className="flex-1">
                          <Button variant="outline" className="w-full">View Results</Button>
                        </Link>
                        <Link to={`/assessments/${assessment.id}`} className="flex-1">
                          <Button className="w-full bg-mind-purple hover:bg-mind-purple-dark/90">Take Again</Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-mind-gray mb-4">You haven't completed any assessments yet.</p>
              <Link to="/assessments">
                <Button>Browse Available Assessments</Button>
              </Link>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
};

export default Assessments;
