
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import DashboardLayout from "@/components/DashboardLayout";
import { BarChart, FileCheck, Book, PenTool } from "lucide-react";
import { Link } from "react-router-dom";

const Dashboard = () => {
  return (
    <DashboardLayout>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-mind-gray-dark">Welcome back, Alex</h1>
        <p className="text-mind-gray mt-1">Here's an overview of your journey so far.</p>
      </header>
      
      {/* Quick actions */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4 text-mind-gray-dark">Quick actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link to="/assessments">
            <Card className="card-hover h-full">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="bg-mind-blue-light p-3 rounded-full">
                  <FileCheck className="text-mind-blue-dark" size={24} />
                </div>
                <div>
                  <h3 className="font-medium">Start your weekly check-in</h3>
                  <p className="text-sm text-mind-gray">Track your mood and anxiety levels</p>
                </div>
              </CardContent>
            </Card>
          </Link>
          
          <Link to="/modules/anxiety">
            <Card className="card-hover h-full">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="bg-mind-purple-light p-3 rounded-full">
                  <Book className="text-mind-purple-dark" size={24} />
                </div>
                <div>
                  <h3 className="font-medium">Continue Anxiety Toolkit</h3>
                  <p className="text-sm text-mind-gray">You're 60% through this module</p>
                </div>
              </CardContent>
            </Card>
          </Link>
          
          <Link to="/journal">
            <Card className="card-hover h-full">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="bg-mind-blue-light p-3 rounded-full">
                  <PenTool className="text-mind-blue-dark" size={24} />
                </div>
                <div>
                  <h3 className="font-medium">Write in your journal</h3>
                  <p className="text-sm text-mind-gray">Record your thoughts and reflections</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      </section>
      
      {/* Recent insights */}
      <section className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-mind-gray-dark">Recent insights</h2>
          <Link to="/insights">
            <Button variant="ghost" className="text-mind-purple-dark hover:text-mind-purple-dark/90 hover:bg-mind-purple-light/50">
              View all
            </Button>
          </Link>
        </div>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Anxiety level trends</CardTitle>
            <CardDescription>
              Based on your weekly check-ins over the past month
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <div className="h-[120px] flex items-end gap-2">
              <div className="w-full flex items-end gap-2">
                <div className="h-[40%] w-1/4 bg-mind-blue rounded-sm"></div>
                <div className="h-[65%] w-1/4 bg-mind-blue rounded-sm"></div>
                <div className="h-[50%] w-1/4 bg-mind-blue rounded-sm"></div>
                <div className="h-[35%] w-1/4 bg-mind-blue rounded-sm"></div>
              </div>
            </div>
            <div className="flex justify-between mt-3 text-sm text-mind-gray">
              <div>Week 1</div>
              <div>Week 2</div>
              <div>Week 3</div>
              <div>Week 4</div>
            </div>
            <div className="mt-4 text-sm">
              <p className="text-mind-gray-dark">
                <span className="font-medium">Great progress!</span> Your anxiety levels have shown a 
                <span className="text-green-600"> 15% decrease</span> over the past month.
              </p>
            </div>
          </CardContent>
        </Card>
      </section>
      
      {/* Current modules */}
      <section className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-mind-gray-dark">Your active modules</h2>
          <Link to="/modules">
            <Button variant="ghost" className="text-mind-purple-dark hover:text-mind-purple-dark/90 hover:bg-mind-purple-light/50">
              Browse all
            </Button>
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex flex-col">
                  <h3 className="font-semibold">Anxiety Toolkit</h3>
                  <p className="text-sm text-mind-gray">Understanding and managing anxiety</p>
                </div>
                <div className="bg-mind-purple-light h-10 w-10 rounded-full flex items-center justify-center">
                  <span className="text-mind-purple-dark font-medium text-sm">60%</span>
                </div>
              </div>
              
              <div className="mt-4">
                <Progress value={60} className="h-2 bg-mind-gray-light" />
              </div>
              
              <div className="mt-4">
                <Link to="/modules/anxiety">
                  <Button className="w-full bg-mind-purple hover:bg-mind-purple-dark text-white">Continue</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-hover">
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div className="flex flex-col">
                  <h3 className="font-semibold">Cognitive Bias Awareness</h3>
                  <p className="text-sm text-mind-gray">Identifying thinking patterns</p>
                </div>
                <div className="bg-mind-blue-light h-10 w-10 rounded-full flex items-center justify-center">
                  <span className="text-mind-blue-dark font-medium text-sm">30%</span>
                </div>
              </div>
              
              <div className="mt-4">
                <Progress value={30} className="h-2 bg-mind-gray-light" />
              </div>
              
              <div className="mt-4">
                <Link to="/modules/bias">
                  <Button className="w-full bg-mind-blue hover:bg-mind-blue-dark text-white">Continue</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
      
      {/* Crisis support reminder */}
      <section>
        <div className="crisis-support">
          <div className="flex items-start gap-3">
            <div className="font-bold">Need immediate help?</div>
            <div>
              If you're experiencing a mental health crisis, please reach out for professional support immediately.
              <div className="mt-2">
                <Link to="/resources/crisis" className="underline font-semibold">View crisis resources</Link> or call the National Suicide Prevention Lifeline at <a href="tel:988" className="font-semibold">988</a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </DashboardLayout>
  );
};

export default Dashboard;
