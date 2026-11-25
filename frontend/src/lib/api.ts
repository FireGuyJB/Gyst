// The one place the frontend talks to the Gyst API.
//
// Pages call these typed functions instead of using fetch() directly. That keeps
// URLs, JSON handling and error handling in one file, and if the API changes
// there's one place to update. (Why the browser calls the API directly: see
// docs/decisions/0005-client-side-api-calls.md.)

// NEXT_PUBLIC_ variables are copied into the browser's JavaScript when the app
// is built or the dev server starts. Set it in frontend/.env.local to override.
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** A goal, as the API returns it (matches GoalRead in backend/app/schemas.py). */
export type Goal = {
  id: number;
  title: string;
  created_at: string; // ISO 8601 timestamp in UTC, e.g. "2026-11-24T22:09:40Z"
};

/** A supporting goal in one of the 8 slots (matches SupportingGoalRead). */
export type SupportingGoal = {
  id: number;
  goal_id: number;
  position: number; // 0-7, clockwise from the top-left of the grid
  title: string;
};

/** A goal with its supporting goals (matches GoalDetail). Empty slots are missing. */
export type GoalDetail = Goal & { supporting_goals: SupportingGoal[] };

/** The API couldn't be reached at all: it's not running, or the network is down. */
export class ApiUnreachableError extends Error {
  constructor() {
    super("Can't reach the Gyst API");
    this.name = "ApiUnreachableError";
  }
}

/** The API answered, but with an error status (e.g. 422 for invalid input). */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    // fetch() only throws when no response came back at all.
    throw new ApiUnreachableError();
  }

  if (!response.ok) {
    throw new ApiError(response.status, `The API returned ${response.status}`);
  }
  // 204 No Content (e.g. after a DELETE) has no body to parse.
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

/** Turn any error from this file into a sentence for the user. */
export function describeError(error: unknown, invalidInput: string): string {
  if (error instanceof ApiUnreachableError) {
    return "Can't reach the Gyst API. Is the backend running?";
  }
  if (error instanceof ApiError && error.status === 422) {
    return invalidInput;
  }
  return "Something went wrong. Please try again.";
}

/** GET /goals: all goals, newest first. */
export function listGoals(): Promise<Goal[]> {
  return request<Goal[]>("/goals");
}

/** POST /goals: save a new goal. The API trims the title and checks its length. */
export function createGoal(title: string): Promise<Goal> {
  return request<Goal>("/goals", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

/** GET /goals/{id}: one goal with its supporting goals. */
export function getGoal(id: string | number): Promise<GoalDetail> {
  return request<GoalDetail>(`/goals/${id}`);
}

/** PUT /goals/{id}/supporting-goals/{position}: fill a slot or rename it. */
export function setSupportingGoal(
  goalId: number,
  position: number,
  title: string,
): Promise<SupportingGoal> {
  return request<SupportingGoal>(`/goals/${goalId}/supporting-goals/${position}`, {
    method: "PUT",
    body: JSON.stringify({ title }),
  });
}

/** DELETE /goals/{id}/supporting-goals/{position}: empty a slot. */
export function clearSupportingGoal(goalId: number, position: number): Promise<void> {
  return request<void>(`/goals/${goalId}/supporting-goals/${position}`, { method: "DELETE" });
}
