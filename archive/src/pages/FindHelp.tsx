import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  MapPin, 
  Phone, 
  Globe, 
  Clock, 
  Star, 
  Search, 
  Filter,
  ExternalLink,
  Heart,
  Brain,
  Users,
  Shield,
  AlertTriangle,
  ArrowLeft
} from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";

const professionalTypes = [
  { value: "psychiatrist", label: "Psychiatrists", description: "Medical doctors who can prescribe medication and provide therapy" },
  { value: "psychologist", label: "Psychologists", description: "Mental health professionals who provide therapy and psychological testing" },
  { value: "therapist", label: "Licensed Therapists", description: "Counselors specializing in various therapeutic approaches" },
  { value: "counselor", label: "Mental Health Counselors", description: "Professionals providing counseling for various mental health concerns" },
  { value: "social-worker", label: "Clinical Social Workers", description: "Licensed professionals providing therapy and case management" }
];

const specializations = [
  "Anxiety Disorders", "Depression", "Trauma/PTSD", "Addiction", "Eating Disorders",
  "Relationship Issues", "Grief/Loss", "ADHD", "Bipolar Disorder", "OCD",
  "Teen/Adolescent", "Family Therapy", "Couples Therapy", "Group Therapy"
];

const insuranceProviders = [
  "Aetna", "Blue Cross Blue Shield", "Cigna", "Humana", "Kaiser Permanente",
  "Medicaid", "Medicare", "UnitedHealth", "Self-Pay", "Sliding Scale"
];

const crisisResources = [
  {
    name: "National Suicide Prevention Lifeline",
    phone: "988",
    description: "24/7 free and confidential support for people in distress",
    website: "suicidepreventionlifeline.org",
    available: "24/7"
  },
  {
    name: "Crisis Text Line",
    phone: "Text HOME to 741741",
    description: "Free, 24/7 crisis support via text message",
    website: "crisistextline.org",
    available: "24/7"
  },
  {
    name: "SAMHSA National Helpline",
    phone: "1-800-662-4357",
    description: "Treatment referral and information service",
    website: "samhsa.gov",
    available: "24/7"
  },
  {
    name: "National Domestic Violence Hotline",
    phone: "1-800-799-7233",
    description: "Support for domestic violence situations",
    website: "thehotline.org",
    available: "24/7"
  }
];

const sampleProviders = [
  {
    id: 1,
    name: "Dr. Sarah Johnson",
    type: "Psychiatrist",
    specializations: ["Anxiety Disorders", "Depression", "ADHD"],
    location: "Downtown Medical Center",
    address: "123 Main St, Suite 200",
    phone: "(555) 123-4567",
    website: "drjohnsonpsychiatry.com",
    rating: 4.8,
    reviewCount: 127,
    acceptsInsurance: ["Blue Cross Blue Shield", "Aetna", "UnitedHealth"],
    accepting: true,
    telehealth: true,
    distance: "2.3 miles"
  },
  {
    id: 2,
    name: "Dr. Michael Chen",
    type: "Psychologist",
    specializations: ["Trauma/PTSD", "Anxiety Disorders", "Couples Therapy"],
    location: "Wellness Psychology Group",
    address: "456 Oak Ave, Building B",
    phone: "(555) 234-5678",
    website: "wellnesspsychgroup.com",
    rating: 4.9,
    reviewCount: 89,
    acceptsInsurance: ["Cigna", "Medicaid", "Self-Pay"],
    accepting: true,
    telehealth: true,
    distance: "1.8 miles"
  },
  {
    id: 3,
    name: "Emily Rodriguez, LCSW",
    type: "Clinical Social Worker",
    specializations: ["Depression", "Grief/Loss", "Teen/Adolescent"],
    location: "Community Mental Health Center",
    address: "789 Pine St, Floor 3",
    phone: "(555) 345-6789",
    website: "communitymhc.org",
    rating: 4.7,
    reviewCount: 203,
    acceptsInsurance: ["Medicaid", "Medicare", "Sliding Scale"],
    accepting: false,
    telehealth: true,
    distance: "0.9 miles"
  },
  {
    id: 4,
    name: "Dr. Lisa Park",
    type: "Licensed Therapist",
    specializations: ["Eating Disorders", "Body Image", "Anxiety Disorders"],
    location: "Serenity Counseling Services",
    address: "321 Elm St, Suite 105",
    phone: "(555) 456-7890",
    website: "serenitycounseling.com",
    rating: 4.6,
    reviewCount: 156,
    acceptsInsurance: ["Blue Cross Blue Shield", "Self-Pay"],
    accepting: true,
    telehealth: false,
    distance: "3.2 miles"
  }
];

const FindHelp = () => {
  const [searchLocation, setSearchLocation] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [selectedSpecialization, setSelectedSpecialization] = useState("");
  const [selectedInsurance, setSelectedInsurance] = useState("");
  const [acceptingOnly, setAcceptingOnly] = useState(false);
  const [telehealthOnly, setTelehealthOnly] = useState(false);
  const [activeTab, setActiveTab] = useState("professionals");

  const filteredProviders = sampleProviders.filter(provider => {
    if (selectedType && selectedType !== "all" && provider.type !== selectedType) return false;
    if (selectedSpecialization && selectedSpecialization !== "all" && !provider.specializations.includes(selectedSpecialization)) return false;
    if (selectedInsurance && selectedInsurance !== "all" && !provider.acceptsInsurance.includes(selectedInsurance)) return false;
    if (acceptingOnly && !provider.accepting) return false;
    if (telehealthOnly && !provider.telehealth) return false;
    return true;
  });

  return (
    <DashboardLayout>
      <div className="mb-8">
        <Link to="/resources" className="text-mind-blue-dark hover:underline mb-4 inline-block">
          ← Back to Resources
        </Link>
        <h1 className="text-3xl font-bold text-mind-gray-dark">Find Help</h1>
        <p className="text-mind-gray mt-1">
          Connect with mental health professionals and access crisis resources
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="professionals">Mental Health Professionals</TabsTrigger>
          <TabsTrigger value="crisis">Crisis Resources</TabsTrigger>
          <TabsTrigger value="support">Support Groups</TabsTrigger>
        </TabsList>

        <TabsContent value="professionals" className="mt-6">
          {/* Search and Filters */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Find Mental Health Professionals
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                <div>
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    placeholder="Enter city, state, or ZIP"
                    value={searchLocation}
                    onChange={(e) => setSearchLocation(e.target.value)}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="provider-type">Provider Type</Label>
                  <Select value={selectedType} onValueChange={setSelectedType}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All types</SelectItem>
                      {professionalTypes.map((type) => (
                        <SelectItem key={type.value} value={type.label}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="specialization">Specialization</Label>
                  <Select value={selectedSpecialization} onValueChange={setSelectedSpecialization}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="All specializations" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All specializations</SelectItem>
                      {specializations.map((spec) => (
                        <SelectItem key={spec} value={spec}>
                          {spec}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="insurance">Insurance</Label>
                  <Select value={selectedInsurance} onValueChange={setSelectedInsurance}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="All insurance" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All insurance</SelectItem>
                      {insuranceProviders.map((provider) => (
                        <SelectItem key={provider} value={provider}>
                          {provider}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center space-x-4 mt-6">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={acceptingOnly}
                      onChange={(e) => setAcceptingOnly(e.target.checked)}
                      className="rounded"
                    />
                    <span className="text-sm">Accepting new patients</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={telehealthOnly}
                      onChange={(e) => setTelehealthOnly(e.target.checked)}
                      className="rounded"
                    />
                    <span className="text-sm">Telehealth available</span>
                  </label>
                </div>
              </div>

              <Button className="w-full md:w-auto">
                <Search className="mr-2 h-4 w-4" />
                Search Providers
              </Button>
            </CardContent>
          </Card>

          {/* Provider Types Guide */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Types of Mental Health Professionals</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {professionalTypes.map((type) => (
                  <div key={type.value} className="border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">{type.label}</h4>
                    <p className="text-sm text-mind-gray">{type.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Search Results */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">
                {filteredProviders.length} providers found
              </h3>
              <Button variant="outline" size="sm">
                <Filter className="mr-2 h-4 w-4" />
                More Filters
              </Button>
            </div>

            {filteredProviders.map((provider) => (
              <Card key={provider.id}>
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-mind-gray-dark">{provider.name}</h3>
                      <p className="text-mind-gray">{provider.type}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm font-medium">{provider.rating}</span>
                          <span className="text-sm text-mind-gray">({provider.reviewCount} reviews)</span>
                        </div>
                        {provider.accepting && (
                          <Badge variant="secondary" className="bg-green-100 text-green-700">
                            Accepting new patients
                          </Badge>
                        )}
                        {provider.telehealth && (
                          <Badge variant="outline">Telehealth</Badge>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-sm text-mind-gray mb-1">
                        <MapPin className="h-4 w-4" />
                        {provider.distance}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm font-medium text-mind-gray-dark mb-1">Specializations</p>
                      <div className="flex flex-wrap gap-1">
                        {provider.specializations.map((spec) => (
                          <Badge key={spec} variant="outline" className="text-xs">
                            {spec}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div>
                      <p className="text-sm font-medium text-mind-gray-dark mb-1">Insurance Accepted</p>
                      <div className="flex flex-wrap gap-1">
                        {provider.acceptsInsurance.slice(0, 3).map((insurance) => (
                          <Badge key={insurance} variant="outline" className="text-xs">
                            {insurance}
                          </Badge>
                        ))}
                        {provider.acceptsInsurance.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{provider.acceptsInsurance.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 mb-4 text-sm text-mind-gray">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {provider.location}
                    </div>
                    <div className="flex items-center gap-1">
                      <Phone className="h-4 w-4" />
                      {provider.phone}
                    </div>
                    {provider.website && (
                      <div className="flex items-center gap-1">
                        <Globe className="h-4 w-4" />
                        <a href={`https://${provider.website}`} className="hover:underline">
                          {provider.website}
                        </a>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-3">
                    <Button size="sm">
                      <Phone className="mr-2 h-4 w-4" />
                      Call Now
                    </Button>
                    <Button variant="outline" size="sm">
                      View Profile
                    </Button>
                    {provider.website && (
                      <Button variant="outline" size="sm">
                        <ExternalLink className="mr-2 h-4 w-4" />
                        Website
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="crisis" className="mt-6">
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="bg-red-100 p-3 rounded-full">
                  <AlertTriangle className="text-red-600" size={24} />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-red-700 mb-2">Crisis Support</h2>
                  <p className="text-red-600 mb-4">
                    If you're experiencing a mental health crisis or having thoughts of suicide, please reach out for help immediately. You are not alone.
                  </p>
                  <div className="flex gap-3">
                    <Button className="bg-red-600 hover:bg-red-700">
                      <Phone className="mr-2 h-4 w-4" />
                      Call 988 Now
                    </Button>
                    <Button variant="outline" className="border-red-600 text-red-600 hover:bg-red-50">
                      Text HOME to 741741
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {crisisResources.map((resource, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-lg">{resource.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-mind-gray text-sm mb-4">{resource.description}</p>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-mind-gray" />
                      <span className="font-medium">{resource.phone}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-mind-gray" />
                      <span>{resource.available}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4 text-mind-gray" />
                      <a href={`https://${resource.website}`} className="text-mind-blue-dark hover:underline">
                        {resource.website}
                      </a>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" className="flex-1">
                      <Phone className="mr-2 h-4 w-4" />
                      Call
                    </Button>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Website
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Additional Resources</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <Shield className="mx-auto h-8 w-8 text-mind-blue-dark mb-2" />
                  <h4 className="font-medium mb-1">Safety Planning</h4>
                  <p className="text-sm text-mind-gray">Create a personalized safety plan</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <Heart className="mx-auto h-8 w-8 text-mind-purple-dark mb-2" />
                  <h4 className="font-medium mb-1">Coping Strategies</h4>
                  <p className="text-sm text-mind-gray">Learn healthy coping techniques</p>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <Users className="mx-auto h-8 w-8 text-mind-blue-dark mb-2" />
                  <h4 className="font-medium mb-1">Support Network</h4>
                  <p className="text-sm text-mind-gray">Build your support system</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="support" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Support Groups
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Users className="mx-auto h-12 w-12 text-mind-gray mb-4" />
                <h3 className="text-lg font-medium text-mind-gray-dark mb-2">Support Groups Directory</h3>
                <p className="text-mind-gray mb-4">
                  Connect with others who understand your journey. Support groups provide a safe space to share experiences and learn from one another.
                </p>
                <Button variant="outline">Coming Soon</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
};

export default FindHelp;
