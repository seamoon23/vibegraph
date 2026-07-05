export type SessionSource = 'claude' | 'chatgpt' | 'gemini' | 'manual' | 'unknown';
export type MessageRole = 'user' | 'assistant' | 'system' | 'unknown';

export interface VibeMessage {
  role: MessageRole;
  text: string;
  order: number;
}

export interface VibeScores {
  oneShot: number;
  context: number;
  control: number;
  clarity: number;
}

export interface CapturedConversation {
  source: SessionSource;
  title: string;
  url: string;
  capturedAt: string;
  messages: VibeMessage[];
}

export interface VibeSession extends CapturedConversation {
  id: string;
  project: string;
  task: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  scores?: VibeScores;
  summary?: string;
  notes?: string;
  promptSmells?: string[];
  goodExamples?: string[];
  badExamples?: string[];
  nextActions?: string[];
}

export type CaptureResponse =
  | {
      ok: true;
      conversation: CapturedConversation;
    }
  | {
      ok: false;
      unsupported?: boolean;
      reason: string;
      title?: string;
      url?: string;
    };

export interface ExtensionSettings {
  onboardingDismissed: boolean;
  privacyNoticeCollapsed: boolean;
  overallReportMarkdown?: string;
  overallReportUpdatedAt?: string;
}
