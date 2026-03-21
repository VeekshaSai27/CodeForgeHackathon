import { runPython } from "./pyodideWorker";

function runJavaScript(code: string): Promise<string> {
  return new Promise((resolve) => {
    const iframe = document.createElement("iframe");
    iframe.setAttribute("sandbox", "allow-scripts");
    iframe.style.display = "none";
    document.body.appendChild(iframe);

    const timeout = setTimeout(() => {
      cleanup();
      resolve("Error: Execution timed out (5s)");
    }, 5000);

    function cleanup() {
      clearTimeout(timeout);
      window.removeEventListener("message", onMessage);
      document.body.removeChild(iframe);
    }

    function onMessage(e: MessageEvent) {
      if (e.source !== iframe.contentWindow) return;
      cleanup();
      resolve(e.data?.output ?? "(no output)");
    }

    window.addEventListener("message", onMessage);

    // Inject runner script into the sandboxed iframe
    const script = `
      const logs = [];
      const _log = console.log;
      console.log = (...args) => {
        logs.push(args.map(a => typeof a === "string" ? a : JSON.stringify(a)).join(" "));
      };
      try {
        const result = (function() { ${code} })();
        if (result !== undefined) logs.push(String(result));
        parent.postMessage({ output: logs.join("\\n") || "(no output)" }, "*");
      } catch(e) {
        parent.postMessage({ output: "Error: " + e.message }, "*");
      } finally {
        console.log = _log;
      }
    `;

    const iframeDoc = iframe.contentDocument!;
    iframeDoc.open();
    iframeDoc.write(`<script>${script}<\/script>`);
    iframeDoc.close();
  });
}

export async function runCode(code: string, language = "javascript"): Promise<string> {
  if (language === "python") return runPython(code);
  return runJavaScript(code);
}
