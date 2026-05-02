
import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  FileCheck,
  PenTool,
  BookOpen,
  Users,
  Heart,
  Settings
} from "lucide-react";
import { cn } from "@/lib/utils";

const Sidebar = () => {
  const { pathname } = useLocation();
  
  const menuItems = [
    { label: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
    { label: "Assessments", icon: FileCheck, path: "/assessments" },
    { label: "Modules", icon: BookOpen, path: "/modules" },
    { label: "Journal", icon: PenTool, path: "/journal" },
    { label: "Community", icon: Users, path: "/community" },
    { label: "Resources", icon: Heart, path: "/resources" },
    { label: "Settings", icon: Settings, path: "/settings" },
  ];
  
  return (
    <aside className="h-screen w-64 border-r bg-sidebar fixed left-0 top-0 overflow-y-auto">
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold text-mind-purple-dark">MindNavigator</h2>
      </div>
      
      <nav className="p-2">
        <ul className="space-y-1">
          {menuItems.map((item) => (
            <li key={item.label}>
              <Link
                to={item.path}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 transition-colors",
                  pathname === item.path
                    ? "bg-mind-purple-light text-mind-purple-dark font-medium"
                    : "text-mind-gray-dark hover:bg-mind-purple-light/50 hover:text-mind-purple-dark"
                )}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
        
        <div className="mt-6 px-3">
          <div className="crisis-support">
            <strong>Need help now?</strong>
            <div className="mt-1">
              <Link to="/resources" className="text-red-700 underline">
                Access Crisis Support
              </Link>
            </div>
          </div>
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar;
