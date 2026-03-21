export function runCode(code: string): string {
  const logs: string[] = [];
  const originalConsoleLog = console.log;

  try {
    console.log = (...args: unknown[]) => {
      const message = args
        .map((arg) => {
          if (typeof arg === "string") return arg;
          try {
            return JSON.stringify(arg);
          } catch {
            return String(arg);
          }
        })
        .join(" ");
      logs.push(message);
    };

    const fn = new Function(code);
    const result = fn();

    if (result !== undefined) {
      logs.push(String(result));
    }

    return logs.join("\n");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return `Error: ${message}`;
  } finally {
    console.log = originalConsoleLog;
  }
}
