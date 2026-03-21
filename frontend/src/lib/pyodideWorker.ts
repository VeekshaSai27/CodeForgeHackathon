const workerCode = `
self.importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js");

let pyodide = null;

async function init() {
  pyodide = await loadPyodide();
}

const ready = init();

self.onmessage = async (e) => {
  if (e.data.type === "warmup") {
    await ready;
    self.postMessage({ type: "ready" });
    return;
  }
  await ready;
  const { id, code } = e.data;
  try {
    pyodide.runPython(\`
import sys, io
_stdout = io.StringIO()
sys.stdout = _stdout
\`);
    pyodide.runPython(code);
    const output = pyodide.runPython("_stdout.getvalue()");
    self.postMessage({ id, output: output || "(no output)" });
  } catch (err) {
    self.postMessage({ id, output: \`Error: \${err.message}\` });
  } finally {
    pyodide.runPython("sys.stdout = sys.__stdout__");
  }
};
`;

const blob = new Blob([workerCode], { type: "application/javascript" });
const workerUrl = URL.createObjectURL(blob);
const worker = new Worker(workerUrl);

let _id = 0;
const pending = new Map<number, (output: string) => void>();

worker.onmessage = (e) => {
  if (e.data.type === "ready") {
    pending.get(-1)?.("ready");
    pending.delete(-1);
    return;
  }
  const { id, output } = e.data;
  pending.get(id)?.(output);
  pending.delete(id);
};

export function warmupPyodide(): Promise<void> {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      pending.delete(-1);
      reject(new Error("Pyodide load timed out (30s)"));
    }, 30000);
    pending.set(-1, () => {
      clearTimeout(timeout);
      resolve();
    });
    worker.postMessage({ type: "warmup" });
  });
}

export function runPython(code: string): Promise<string> {
  return new Promise((resolve) => {
    const id = _id++;
    const timeout = setTimeout(() => {
      pending.delete(id);
      resolve("Error: Execution timed out (10s)");
    }, 10000);
    pending.set(id, (output) => {
      clearTimeout(timeout);
      resolve(output);
    });
    worker.postMessage({ id, code });
  });
}
