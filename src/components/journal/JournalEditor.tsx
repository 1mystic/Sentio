
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { CalendarIcon, HelpCircle } from "lucide-react";
import { format } from "date-fns";

interface JournalEditorProps {
  date: Date;
  setDate: (date: Date) => void;
  journalContent: string;
  setJournalContent: (content: string) => void;
  prompt: string;
  onPromptChange: () => void;
  onSave: () => void;
  isSaving: boolean;
}

const JournalEditor = ({
  date,
  setDate,
  journalContent,
  setJournalContent,
  prompt,
  onPromptChange,
  onSave,
  isSaving,
}: JournalEditorProps) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <div className="lg:col-span-3">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="font-semibold">{format(date, "MMMM d, yyyy")}</div>
              <Button 
                variant="ghost" 
                className="flex items-center text-mind-purple-dark hover:text-mind-purple-dark/90"
                onClick={onPromptChange}
              >
                <HelpCircle size={16} className="mr-1" />
                <span>Change Prompt</span>
              </Button>
            </div>
            <div className="italic text-mind-gray">{prompt}</div>
          </CardHeader>
          
          <CardContent>
            <Textarea
              value={journalContent}
              onChange={(e) => setJournalContent(e.target.value)}
              placeholder="Start writing here..."
              className="min-h-[300px]"
            />
            
            <div className="mt-4">
              <Button 
                onClick={onSave} 
                disabled={!journalContent.trim() || isSaving}
                className="bg-mind-purple-dark hover:bg-mind-purple-dark/90"
              >
                {isSaving ? "Saving..." : "Save Entry"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div>
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center justify-center mb-2">
              <CalendarIcon size={18} className="mr-2 text-mind-purple-dark" />
              <span>Select date</span>
            </div>
            <Calendar
              mode="single"
              selected={date}
              onSelect={(date) => date && setDate(date)}
              className="mx-auto"
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default JournalEditor;
