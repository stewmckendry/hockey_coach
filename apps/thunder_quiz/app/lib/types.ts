export type QuestionType = "multiple-choice" | "true-false" | "short-answer";

export type QuestionCategory = 
  | "rules-penalties"
  | "team-systems"
  | "nhl-knowledge"
  | "equipment-safety"
  | "sportsmanship";

export interface Question {
  id: string;
  category: QuestionCategory;
  type: QuestionType;
  question: string;
  options?: string[]; // For multiple choice
  correctAnswer: string | boolean; // String for MC/short answer, boolean for T/F
  hint?: string;
  explanation?: string;
  difficulty: "easy" | "medium" | "hard";
  topics?: string[]; // Topics for diversity tracking
  ageAppropriate?: boolean;
  estimatedReadingTime?: number;
}

export interface GameState {
  nickname: string;
  currentPeriod: number;
  currentQuestion: number;
  playerGoals: number;
  opponentGoals: number;
  questions: Question[];
  answers: Answer[];
  isOvertime: boolean;
  gameStatus: "not-started" | "in-progress" | "finished";
  startTime?: Date;
  endTime?: Date;
  correctStreak: number;
  correctAnswers: number;
  totalQuestions: number;
}

export interface Answer {
  questionId: string;
  userAnswer: string | boolean;
  isCorrect: boolean;
  usedHint: boolean;
  timeSpent: number; // in seconds
}

export interface LeaderboardEntry {
  id: string;
  nickname: string;
  playerGoals: number;
  opponentGoals: number;
  totalQuestions: number;
  accuracy: number;
  date: Date;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}