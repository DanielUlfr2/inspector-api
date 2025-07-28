export const ROLES = {
  ADMIN: "admin",
  USER: "user",
} as const;

export type UserRole = typeof ROLES[keyof typeof ROLES]; 