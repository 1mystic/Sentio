
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PenTool } from "lucide-react";
import { format } from "date-fns";
import type { JournalEntry as JournalEntryType } from '@/services/journalService'; // Renamed to avoid conflict
import { Skeleton } from '@/components/ui/skeleton';

interface PastEntriesProps {
  entries: JournalEntryType[] | undefined;
  isLoading: boolean;
  isError: boolean;
  onWriteClick: () => void;
  onSelectEntry: (entry: JournalEntryType) => void; // Kept as per subtask instructions
}

const PastEntries = ({ entries, isLoading, isError, onWriteClick, onSelectEntry }: PastEntriesProps) => {
  if (isLoading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <Skeleton className="h-5 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2 mb-3" />
              <Skeleton className="h-12 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive mb-4">Failed to load journal entries. Please try again later.</p>
        {/* Optionally, add a retry button here */}
      </div>
    );
  }

  if (!entries || entries.length === 0) {
    return (
      <div className="text-center py-12">
        <PenTool size={48} className="mx-auto mb-4 text-mind-gray" />
        <p className="text-mind-gray mb-4">You haven't written any journal entries yet.</p>
        <Button onClick={onWriteClick}>
          Write Your First Entry
        </Button>
      </div>
    );
  }

  return (
    <>
      {entries.length > 0 ? (
        <div className="space-y-6">
          {entries.map((entry) => (
            <Card key={entry.id} className="card-hover">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-grow cursor-pointer" onClick={() => onSelectEntry(entry)}>
                    <div className="font-semibold mb-1">
                      {/* Dates from Supabase 'date' type are 'YYYY-MM-DD'. Need to replace '-' for cross-browser new Date() compatibility. */}
                      {format(new Date(entry.date.replace(/-/g, '/')), "MMMM d, yyyy")}
                    </div>
                    <div className="italic text-sm text-mind-gray mb-3">
                      Prompt: {entry.prompt || "No prompt"}
                    </div>
                    <p className="text-mind-gray-dark line-clamp-3">{entry.content}</p>
                  </div>
                  {/* The "View" button could also call onSelectEntry, or a different handler if needed */}
                  <Button variant="outline" className="flex-shrink-0" onClick={() => onSelectEntry(entry)}>View</Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        // This case should be covered by the check above, but kept for structural similarity
        <div className="text-center py-12">
          <PenTool size={48} className="mx-auto mb-4 text-mind-gray" />
          <p className="text-mind-gray mb-4">You haven't written any journal entries yet.</p>
          <Button onClick={onWriteClick}>
            Write Your First Entry
          </Button>
        </div>
      )}
    </>
  );
};

export default PastEntries;
