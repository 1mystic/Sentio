
import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="bg-white border-t">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between">
          <div className="mb-6 md:mb-0">
            <h3 className="text-lg font-semibold text-mind-purple-dark">MindNavigator</h3>
            <p className="text-sm text-mind-gray mt-2 max-w-md">
              A self-help tool designed to help identify cognitive biases, manage anxiety, and improve mental wellbeing.
            </p>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-8">
            <div>
              <h4 className="font-medium text-mind-gray-dark mb-4">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/resources" className="text-mind-gray hover:text-mind-purple-dark">
                    Mental Health Resources
                  </Link>
                </li>
                <li>
                  <Link to="/resources/crisis" className="text-destructive font-medium">
                    Crisis Support
                  </Link>
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-mind-gray-dark mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/about" className="text-mind-gray hover:text-mind-purple-dark">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link to="/contact" className="text-mind-gray hover:text-mind-purple-dark">
                    Contact
                  </Link>
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-mind-gray-dark mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/terms" className="text-mind-gray hover:text-mind-purple-dark">
                    Terms of Use
                  </Link>
                </li>
                <li>
                  <Link to="/privacy" className="text-mind-gray hover:text-mind-purple-dark">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link to="/disclaimer" className="text-mind-gray hover:text-mind-purple-dark">
                    Disclaimer
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="crisis-support mt-6 text-center">
          <strong>Need immediate help?</strong> If you're in crisis, please call the National Suicide Prevention Lifeline at <a href="tel:988" className="underline font-bold">988</a> or text HOME to 741741
        </div>
        
        <div className="border-t mt-6 pt-6 text-center text-sm text-mind-gray">
          © {new Date().getFullYear()} MindNavigator. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
