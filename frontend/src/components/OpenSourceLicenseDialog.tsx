import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import { ScrollArea } from "../components/ui/scroll-area";

interface License {
  name: string;
  url: string;
  license: string;
  description: string;
}

const licenses: License[] = [
  {
    name: "React",
    url: "https://react.dev",
    license: "MIT",
    description: "A JavaScript library for building user interfaces.",
  },
  {
    name: "Vite",
    url: "https://vitejs.dev",
    license: "MIT",
    description: "Next generation frontend tooling.",
  },
  {
    name: "Tailwind CSS",
    url: "https://tailwindcss.com",
    license: "MIT",
    description: "A utility-first CSS framework.",
  },
  {
    name: "TanStack Router",
    url: "https://tanstack.com/router",
    license: "MIT",
    description: "Type-safe routing for React applications.",
  },
  {
    name: "TanStack Query",
    url: "https://tanstack.com/query",
    license: "MIT",
    description: "Powerful asynchronous state management.",
  },
  {
    name: "Radix UI",
    url: "https://www.radix-ui.com",
    license: "MIT",
    description: "Unstyled, accessible components for building high-quality design systems.",
  },
  {
    name: "Lucide React",
    url: "https://lucide.dev",
    license: "ISC",
    description: "Beautiful & consistent icons.",
  },
  {
    name: "Zod",
    url: "https://zod.dev",
    license: "MIT",
    description: "TypeScript-first schema validation with static type inference.",
  },
  {
    name: "Framer Motion",
    url: "https://www.framer.com/motion",
    license: "MIT",
    description: "A production-ready motion library for React.",
  },
  {
    name: "Sonner",
    url: "https://sonner.emilkowal.ski",
    license: "MIT",
    description: "An opinionated toast component for React.",
  },
  {
    name: "Axios",
    url: "https://axios-http.com",
    license: "MIT",
    description: "Promise based HTTP client for the browser and node.js.",
  },
  {
    name: "date-fns",
    url: "https://date-fns.org",
    license: "MIT",
    description: "Modern JavaScript date utility library.",
  },
];

export function OpenSourceLicenseDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button className="text-sm text-muted-foreground hover:text-[#7ED6E8] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#7ED6E8] rounded-sm">
          Open Source License
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-2xl max-h-[85vh] flex flex-col p-0 overflow-hidden bg-background/95 backdrop-blur-xl border-border/50 shadow-2xl">
        <DialogHeader className="p-6 pb-2 shrink-0">
          <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4] bg-clip-text text-transparent">
            Open Source Licenses
          </DialogTitle>
          <DialogDescription>
            This project is built with the help of these amazing open source libraries.
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 px-6 pb-6 w-full">
          <div className="grid gap-4 pr-4">
            {licenses.map((lib, index) => (
              <div
                key={index}
                className="p-4 rounded-xl border bg-card/50 hover:bg-muted/50 transition-colors space-y-2 group"
              >
                <div className="flex items-center justify-between">
                  <a
                    href={lib.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-semibold text-lg hover:text-[#7ED6E8] transition-colors flex items-center gap-2"
                  >
                    {lib.name}
                  </a>
                  <span className="text-xs font-mono font-medium px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground border">
                    {lib.license}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{lib.description}</p>
                <div className="text-xs text-muted-foreground/50 pt-1 group-hover:text-[#7ED6E8] transition-colors">
                  {lib.url}
                </div>
              </div>
            ))}
          </div>
          <div className="h-6"></div> {/* Bottom spacer */}
        </ScrollArea>

        <div className="p-4 border-t bg-muted/20 shrink-0 text-center text-xs text-muted-foreground">
          Thank you to all the contributors of these projects.
        </div>
      </DialogContent>
    </Dialog>
  );
}
