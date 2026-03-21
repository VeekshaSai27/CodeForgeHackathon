const workerCode = `
self.importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js");

let pyodide = null;

async function init() {
  pyodide = await loadPyodide();
}

const ready = init();

self.onmessage = async (e) => {
  await ready;
  const { id, code } = e.data;
  try {
    // Capture stdout
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
  const { id, output } = e.data;
  pending.get(id)?.(output);
  pending.delete(id);
};

export function runPython(code: string): Promise<string> {
  return new Promise((resolve) => {
    const id = _id++;
    pending.set(id, resolve);
    worker.postMessage({ id, code });
  });
}
