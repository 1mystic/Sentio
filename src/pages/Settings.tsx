
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";

const Settings = () => {
  return (
    <DashboardLayout>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-mind-gray-dark">Settings</h1>
        <p className="text-mind-gray mt-1">Manage your account and preferences</p>
      </header>

      <div className="space-y-6">
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold mb-4">Profile Settings</h2>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Display Name</Label>
                <Input id="name" placeholder="Your name" className="max-w-md" />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" placeholder="Your email" className="max-w-md" />
              </div>
              <Button>Save Changes</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold mb-4">Notifications</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="email-notifications">Email Notifications</Label>
                  <p className="text-sm text-mind-gray">Receive updates and reminders via email</p>
                </div>
                <Switch id="email-notifications" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="weekly-summary">Weekly Summary</Label>
                  <p className="text-sm text-mind-gray">Get a weekly summary of your progress</p>
                </div>
                <Switch id="weekly-summary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold mb-4">Privacy</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="public-profile">Public Profile</Label>
                  <p className="text-sm text-mind-gray">Make your profile visible to other users</p>
                </div>
                <Switch id="public-profile" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="share-progress">Share Progress</Label>
                  <p className="text-sm text-mind-gray">Allow sharing of your progress in the community</p>
                </div>
                <Switch id="share-progress" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold text-red-600 mb-4">Danger Zone</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-mind-gray mb-2">
                  Delete your account and all associated data. This action cannot be undone.
                </p>
                <Button variant="destructive">Delete Account</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
