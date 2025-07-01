
import { useSearchParams } from "react-router-dom";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ChevronLeft, Calendar } from "lucide-react";
import { useEffect, useState } from "react";

interface AssessmentResult {
  id: string;
  title: string;
  date: string;
  category: string;
  summary: string;
  score?: number;
  interpretation: string;
  recommendations: string[];
}

const Insights = () => {
  const [searchParams] = useSearchParams();
  const assessmentId = searchParams.get("id");
  const [results, setResults] = useState<AssessmentResult[]>([]);

  useEffect(() => {
    // In a real app, this would fetch from an API/database
    // Here we're simulating data based on the assessment answers in console logs
    const mockResults: AssessmentResult[] = [
      {
        id: "anxiety",
        title: "GAD-7 Anxiety Screening",
        date: "April 26, 2025",
        category: "Mental Health",
        summary: "Mild anxiety symptoms detected",
        score: 8,
        interpretation: "Your responses indicate mild anxiety symptoms that may benefit from monitoring.",
        recommendations: [
          "Practice daily mindfulness meditation for 5-10 minutes",
          "Consider journaling about stressful situations",
          "Maintain regular physical exercise"
        ]
      },
      {
        id: "biases",
        title: "Cognitive Bias Inventory",
        date: "April 26, 2025",
        category: "Cognitive Patterns",
        summary: "Some confirmation bias tendencies identified",
        interpretation: "Your responses suggest some tendencies toward confirmation bias, which means you may sometimes favor information that confirms your existing beliefs.",
        recommendations: [
          "Practice considering alternative viewpoints when making decisions",
          "Ask for feedback from people with different perspectives",
          "Question your initial assumptions when researching new topics"
        ]
      }
    ];

    setResults(mockResults.filter(result => !assessmentId || result.id === assessmentId));
  }, [assessmentId]);

  return (
    <DashboardLayout>
      <Link to="/assessments">
        <Button variant="ghost" className="mb-6 pl-0 text-mind-gray-dark">
          <ChevronLeft size={18} className="mr-1" /> Back to Assessments
        </Button>
      </Link>
      
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-mind-gray-dark">Your Insights</h1>
        <p className="text-mind-gray mt-1">
          Results and personalized recommendations based on your assessment responses
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {results.map((result) => (
          <Card key={result.id} className="overflow-hidden">
            <CardContent className="p-0">
              <div className="p-6 border-b">
                <div className="flex justify-between items-start mb-3">
                  <Badge variant="outline" className="bg-mind-gray-light">
                    {result.category}
                  </Badge>
                  <div className="flex items-center text-sm text-mind-gray">
                    <Calendar size={14} className="mr-1" />
                    <span>{result.date}</span>
                  </div>
                </div>
                
                <h2 className="text-xl font-semibold mb-2">{result.title}</h2>
                <p className="text-mind-gray-dark font-medium">{result.summary}</p>
                
                {result.score !== undefined && (
                  <div className="mt-4 p-3 bg-mind-gray-light/50 rounded-md">
                    <div className="text-sm text-mind-gray">Score</div>
                    <div className="text-2xl font-bold">{result.score}/21</div>
                  </div>
                )}
              </div>
              
              <div className="p-6 border-b">
                <h3 className="font-medium mb-3">Interpretation</h3>
                <p className="text-mind-gray-dark">{result.interpretation}</p>
              </div>
              
              <div className="p-6">
                <h3 className="font-medium mb-3">Recommendations</h3>
                <ul className="space-y-2">
                  {result.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start">
                      <span className="inline-block h-2 w-2 bg-mind-purple-dark rounded-full mt-2 mr-2"></span>
                      <span>{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {results.length === 0 && (
        <div className="text-center p-12 border rounded-lg">
          <h3 className="text-lg font-medium mb-2">No assessment results found</h3>
          <p className="text-mind-gray mb-4">Complete an assessment to see your personalized insights</p>
          <Link to="/assessments">
            <Button>Browse Assessments</Button>
          </Link>
        </div>
      )}
    </DashboardLayout>
  );
};

export default Insights;
