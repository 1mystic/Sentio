
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Phone, Book, Heart, Compass } from "lucide-react";
import { Link } from "react-router-dom";

const Resources = () => {
  return (
    <DashboardLayout>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-mind-gray-dark">Resources</h1>
        <p className="text-mind-gray mt-1">
          Access helpful resources and support information
        </p>
      </header>

      {/* Crisis Support Section */}
      <section className="mb-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="bg-red-100 p-3 rounded-full">
                <Phone className="text-red-600" size={24} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-red-700 mb-2">Need immediate help?</h2>
                <p className="text-red-600 mb-4">
                  If you're experiencing a mental health crisis, please reach out for professional support immediately.
                </p>
                <div className="space-y-2">
                  <p className="font-medium">24/7 Crisis Hotlines:</p>
                  <ul className="list-disc list-inside space-y-1 text-red-600">
                    <li>National Suicide Prevention Lifeline: <a href="tel:988" className="underline">988</a></li>
                    <li>Crisis Text Line: Text HOME to <span className="font-medium">741741</span></li>
                  </ul>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Resource Categories */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="card-hover">
          <CardContent className="p-6">
            <div className="bg-mind-blue-light p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <Book className="text-mind-blue-dark" size={24} />
            </div>
            <h3 className="font-semibold mb-2">Educational Materials</h3>
            <p className="text-mind-gray text-sm mb-4">
              Articles, guides, and information about mental health topics
            </p>
            <Link to="/resources/education">
              <Button variant="outline" className="w-full">Browse Materials</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="card-hover">
          <CardContent className="p-6">
            <div className="bg-mind-purple-light p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <Heart className="text-mind-purple-dark" size={24} />
            </div>
            <h3 className="font-semibold mb-2">Self-Help Tools</h3>
            <p className="text-mind-gray text-sm mb-4">
              Practical exercises and techniques for emotional wellbeing
            </p>
            <Link to="/resources/self-help">
              <Button variant="outline" className="w-full">Access Tools</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="card-hover">
          <CardContent className="p-6">
            <div className="bg-mind-blue-light p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <Compass className="text-mind-blue-dark" size={24} />
            </div>
            <h3 className="font-semibold mb-2">Find Help</h3>
            <p className="text-mind-gray text-sm mb-4">
              Directory of mental health professionals and services
            </p>
            <Link to="/resources/find-help">
              <Button variant="outline" className="w-full">Find Support</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Resources;
