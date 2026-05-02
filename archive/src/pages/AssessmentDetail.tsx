
import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { ChevronLeft, AlertTriangle } from "lucide-react";
import { toast } from "sonner";

// Sample GAD-7 questions
const anxietyQuestions = [
  {
    id: 1,
    question: "Feeling nervous, anxious, or on edge",
    options: [
      { value: "0", label: "Not at all" },
      { value: "1", label: "Several days" },
      { value: "2", label: "More than half the days" },
      { value: "3", label: "Nearly every day" }
    ]
  },
  {
    id: 2,
    question: "Not being able to stop or control worrying",
    options: [
      { value: "0", label: "Not at all" },
      { value: "1", label: "Several days" },
      { value: "2", label: "More than half the days" },
      { value: "3", label: "Nearly every day" }
    ]
  },
  {
    id: 3,
    question: "Worrying too much about different things",
    options: [
      { value: "0", label: "Not at all" },
      { value: "1", label: "Several days" },
      { value: "2", label: "More than half the days" },
      { value: "3", label: "Nearly every day" }
    ]
  },
  {
    id: 4,
    question: "Trouble relaxing",
    options: [
      { value: "0", label: "Not at all" },
      { value: "1", label: "Several days" },
      { value: "2", label: "More than half the days" },
      { value: "3", label: "Nearly every day" }
    ]
  },
  {
    id: 5,
    question: "Being so restless that it's hard to sit still",
    options: [
      { value: "0", label: "Not at all" },
      { value: "1", label: "Several days" },
      { value: "2", label: "More than half the days" },
      { value: "3", label: "Nearly every day" }
    ]
  }
];

// Sample bias questions
const biasQuestions = [
  {
    id: 1,
    question: "When someone disagrees with me, I often assume they don't have all the facts.",
    options: [
      { value: "0", label: "Strongly disagree" },
      { value: "1", label: "Somewhat disagree" },
      { value: "2", label: "Neither agree nor disagree" },
      { value: "3", label: "Somewhat agree" },
      { value: "4", label: "Strongly agree" }
    ]
  },
  {
    id: 2,
    question: "I tend to search for information that confirms what I already believe.",
    options: [
      { value: "0", label: "Strongly disagree" },
      { value: "1", label: "Somewhat disagree" },
      { value: "2", label: "Neither agree nor disagree" },
      { value: "3", label: "Somewhat agree" },
      { value: "4", label: "Strongly agree" }
    ]
  },
  {
    id: 3,
    question: "I often remember my successful decisions better than my unsuccessful ones.",
    options: [
      { value: "0", label: "Strongly disagree" },
      { value: "1", label: "Somewhat disagree" },
      { value: "2", label: "Neither agree nor disagree" },
      { value: "3", label: "Somewhat agree" },
      { value: "4", label: "Strongly agree" }
    ]
  }
];

const AssessmentDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Determine which assessment to show based on the ID
  const assessmentData = {
    anxiety: {
      title: "GAD-7 Anxiety Screening",
      description: "This brief screening tool helps identify symptoms of generalized anxiety disorder. Over the past 2 weeks, how often have you been bothered by the following problems?",
      questions: anxietyQuestions
    },
    biases: {
      title: "Cognitive Bias Inventory",
      description: "This assessment helps you identify common cognitive biases that may affect your thinking and decision making. Please indicate how much you agree with each statement.",
      questions: biasQuestions
    }
  };
  
  const currentAssessment = id === "anxiety" ? assessmentData.anxiety : 
                           id === "biases" ? assessmentData.biases :
                           assessmentData.anxiety; // Default to anxiety assessment
  
  const questions = currentAssessment.questions;
  
  const handleAnswer = (value: string) => {
    setAnswers({ ...answers, [currentQuestion]: value });
  };
  
  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      submitAssessment();
    }
  };
  
  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const submitAssessment = () => {
    setIsSubmitting(true);
    // In a real app, we would send the data to an API
    console.log("Assessment answers:", answers);
    
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      toast.success("Assessment submitted successfully");
      navigate(`/insights?id=${id}`);
    }, 1000);
  };
  
  const progress = ((currentQuestion + 1) / questions.length) * 100;
  
  return (
    <DashboardLayout>
      <Button 
        variant="ghost" 
        className="mb-6 pl-0 text-mind-gray-dark" 
        onClick={() => navigate("/assessments")}
      >
        <ChevronLeft size={18} className="mr-1" /> Back to Assessments
      </Button>
      
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-mind-gray-dark">{currentAssessment.title}</h1>
        <p className="text-mind-gray mt-1">
          {currentAssessment.description}
        </p>
      </header>
      
      <div className="disclaimer mb-6 flex items-start gap-3">
        <AlertTriangle size={20} />
        <div>
          <strong>Important:</strong> This is a self-screening tool, not a diagnostic test.
          Results should be discussed with a qualified healthcare provider.
        </div>
      </div>
      
      <div className="mb-6">
        <div className="flex justify-between text-sm mb-1">
          <span>Question {currentQuestion + 1} of {questions.length}</span>
          <span>{Math.round(progress)}% complete</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>
      
      <Card className="mb-6">
        <CardContent className="p-6">
          <h2 className="text-lg font-medium mb-6">{questions[currentQuestion].question}</h2>
          
          <RadioGroup 
            value={answers[currentQuestion]} 
            onValueChange={handleAnswer}
            className="space-y-3"
          >
            {questions[currentQuestion].options.map((option) => (
              <div key={option.value} className="flex items-center space-x-2 rounded-md border p-3 hover:bg-mind-gray-light/40">
                <RadioGroupItem value={option.value} id={`option-${option.value}`} />
                <Label htmlFor={`option-${option.value}`} className="flex-grow cursor-pointer">
                  {option.label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>
      
      <div className="flex justify-between">
        <Button 
          variant="outline" 
          onClick={handlePrevious} 
          disabled={currentQuestion === 0}
        >
          Previous
        </Button>
        
        <Button 
          onClick={handleNext} 
          disabled={!answers[currentQuestion] || isSubmitting}
          className="bg-mind-purple-dark hover:bg-mind-purple-dark/90"
        >
          {isSubmitting ? "Submitting..." : (currentQuestion === questions.length - 1 ? "Submit" : "Next")}
        </Button>
      </div>
    </DashboardLayout>
  );
};

export default AssessmentDetail;
