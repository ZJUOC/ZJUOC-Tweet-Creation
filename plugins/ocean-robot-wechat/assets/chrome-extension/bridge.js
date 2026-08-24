(() => {
  const reply = (ok, detail) => window.postMessage({
    source: "ocean-robot-wechat-bridge",
    type: "SET_CONTENT_RESULT",
    ok,
    detail
  }, "*");

  function setEditorContent(content) {
    if (typeof window.mp_editor_set_content === "function") {
      window.mp_editor_set_content(content);
      return true;
    }
    const api = window.__MP_Editor_JSAPI__;
    if (api && typeof api.setContent === "function") {
      api.setContent({ content });
      return true;
    }
    if (api && typeof api.invoke === "function") {
      api.invoke("setContent", { content });
      return true;
    }
    return false;
  }

  window.addEventListener("message", (event) => {
    const data = event.data;
    if (event.source !== window || data?.source !== "ocean-robot-wechat" || data.type !== "SET_CONTENT") return;
    try {
      const ok = setEditorContent(data.html);
      reply(ok, ok ? "content imported" : "editor API unavailable");
    } catch (error) {
      reply(false, String(error));
    }
  });
})();
