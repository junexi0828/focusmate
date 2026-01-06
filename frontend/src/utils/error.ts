

/**
 * Safely extracts a user-friendly error message from an error object.
 * Handles various formats like:
 * - Simple string message
 * - Pydantic validation errors (array of objects)
 * - Axios error objects with response data
 *
 * @param error The error object to parse
 * @param defaultMessage Fallback message if parsing fails
 * @returns A string representation of the error
 */
export const getErrorMessage = (error: any, defaultMessage: string = "알 수 없는 오류가 발생했습니다"): string => {
  if (!error) return defaultMessage;

  // Handle Axios errors
  if (error.response?.data) {
    const data = error.response.data;

    // Check for "detail" field (common in FastAP/Pydantic)
    if (data.detail) {
      // If detail is a string, return it
      if (typeof data.detail === "string") {
        return data.detail;
      }

      // If detail is an array (Pydantic validation errors), join messages
      if (Array.isArray(data.detail)) {
        return data.detail
          .map((err: any) => err.msg || JSON.stringify(err))
          .join("\n");
      }

      // If detail is an object, try to stringify or extract message
      if (typeof data.detail === "object") {
        return JSON.stringify(data.detail);
      }
    }

    // Check for "message" field
    if (data.message && typeof data.message === "string") {
      return data.message;
    }
  }

  // Handle standard Error objects
  if (error instanceof Error) {
    return error.message;
  }

  // Handle string errors
  if (typeof error === "string") {
    return error;
  }

  return defaultMessage;
};
