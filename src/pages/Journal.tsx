import { useState } from "react";
import { format } from "date-fns";
import { useAuth } from "@/contexts/AuthContext"; // Added
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"; // Added
import { getJournalEntries, createJournalEntry } from "@/services/journalService"; // Added
import type { JournalEntry, JournalEntryInsert } from "@/services/journalService"; // Added
import { toast } from "sonner"; // Added

import DashboardLayout from "@/components/DashboardLayout";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Calendar } from "@/components/ui/calendar";
import JournalEditor from "@/components/journal/JournalEditor";
import PastEntries from "@/components/journal/PastEntries";

const Journal = () => {
  const { user } = useAuth(); // Added
  const queryClient = useQueryClient(); // Added

  const [date, setDate] = useState<Date>(new Date());
  const [journalContent, setJournalContent] = useState("");
  const [prompt, setPrompt] = useState("What's on your mind today?");
  const [activeTab, setActiveTab] = useState("write"); // To manage active tab for onWriteClick

  // Prompts can remain as they are
  const prompts = [
    "What's on your mind today?",
    "What are three things you're grateful for today?",
    "Describe a challenge you faced recently and how you handled it.",
    "What values guided your decisions today?",
    "Reflect on something that made you feel anxious and how you responded.",
    "What biases might have influenced your thinking today?"
  ];
  
  const changePrompt = () => {
    const currentIndex = prompts.indexOf(prompt);
    const nextIndex = (currentIndex + 1) % prompts.length;
    setPrompt(prompts[nextIndex]);
  };

  // Fetch journal entries
  const { data: pastEntries, isLoading: isLoadingEntries, isError: isErrorEntries } = useQuery<JournalEntry[], Error>({
    queryKey: ['journalEntries', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      return getJournalEntries(user.id);
    },
    enabled: !!user?.id,
  });

  // Mutation for creating journal entries
  const { mutate: saveEntryMutation, isLoading: isSavingEntry } = useMutation<JournalEntry, Error, JournalEntryInsert>({
    mutationFn: (newEntryData: JournalEntryInsert) => createJournalEntry(newEntryData),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['journalEntries', user?.id] });
      toast.success("Journal entry saved successfully!");
      setJournalContent(""); // Clear content
      // Optionally reset date or prompt, e.g., setDate(new Date()); setPrompt(prompts[0]);
      // If the new entry's date is the currently selected date, it will appear in "Past Entries" if user switches tab.
    },
    onError: (error: Error) => {
      toast.error(`Failed to save journal entry: ${error.message}`);
    },
  });
  
  const handleSave = () => {
    if (!user?.id) {
      toast.error("You must be logged in to save an entry.");
      return;
    }
    const entryData: JournalEntryInsert = {
      date: format(date, "yyyy-MM-dd"), // Ensure this format matches Supabase 'date' type
      content: journalContent,
      prompt,
      user_id: user.id,
    };
    saveEntryMutation(entryData);
  };

  const handleSelectEntry = (entry: JournalEntry) => {
    // Placeholder: Log to console. In a real app, you might navigate or display details.
    console.log("Selected entry:", entry);
    setDate(new Date(entry.date.replace(/-/g, '/'))); // Update current date to selected entry's date
    setJournalContent(entry.content || ""); // Populate editor content
    setPrompt(entry.prompt || prompts[0]); // Populate prompt
    setActiveTab("write"); // Switch to editor tab
    toast.info(`Viewing entry from ${format(new Date(entry.date.replace(/-/g, '/')), "MMMM d, yyyy")}`);
  };
  
  const handleWriteClick = () => {
    setActiveTab("write");
    // Optionally, reset date to today if desired when clicking "Write Your First Entry"
    // setDate(new Date()); 
    // setJournalContent("");
    // setPrompt(prompts[0]);
  };

  return (
    <DashboardLayout>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-mind-gray-dark">Journal</h1>
        <p className="text-mind-gray mt-1">
          Reflect on your thoughts, feelings, and experiences
        </p>
      </header>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-6">
        <TabsList className="mb-6">
          <TabsTrigger value="write">Write</TabsTrigger>
          <TabsTrigger value="past-entries">Past Entries</TabsTrigger>
          <TabsTrigger value="calendar">Calendar View</TabsTrigger>
        </TabsList>
        
        <TabsContent value="write">
          <JournalEditor
            date={date}
            setDate={setDate}
            journalContent={journalContent}
            setJournalContent={setJournalContent}
            prompt={prompt}
            onPromptChange={changePrompt}
            onSave={handleSave}
            isSaving={isSavingEntry} // Passed isSavingEntry
          />
        </TabsContent>
        
        <TabsContent value="past-entries">
          <PastEntries 
            entries={pastEntries}
            isLoading={isLoadingEntries}
            isError={isErrorEntries}
            onSelectEntry={handleSelectEntry} // Added handler
            onWriteClick={handleWriteClick} // Updated handler
          />
        </TabsContent>
        
        <TabsContent value="calendar">
          <Card>
            <CardContent className="py-6">
              <div className="flex justify-center">
                <Calendar
                  mode="single"
                  selected={date}
                  onSelect={(selectedDate) => {
                    if (selectedDate) {
                      setDate(selectedDate);
                      setActiveTab("write"); // Switch to write tab on date selection
                    }
                  }}
                  className="mx-auto"
                  modifiers={{
                    // Ensure pastEntries is not undefined before mapping
                    entry: pastEntries ? pastEntries.map(entry => new Date(entry.date.replace(/-/g, '/'))) : [] 
                  }}
                  modifiersStyles={{
                    entry: { backgroundColor: "hsl(var(--mind-purple))", color: "hsl(var(--mind-purple-foreground))" } // Adjusted for better visibility
                  }}
                />
              </div>
              <div className="mt-4 text-center text-sm text-mind-gray">
                Dates highlighted in purple indicate days with journal entries.
                Click on a date to view or create an entry.
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
};

export default Journal;
