(() => {
  const bridge = document.createElement("script");
  bridge.src = chrome.runtime.getURL("bridge.js");
  bridge.onload = () => bridge.remove();
  (document.head || document.documentElement).appendChild(bridge);

  const button = document.createElement("button");
  button.textContent = "导入海机协推文";
  Object.assign(button.style, {
    position: "fixed",
    right: "18px",
    bottom: "22px",
    zIndex: "2147483647",
    border: "0",
    borderRadius: "999px",
    padding: "11px 16px",
    background: "#8CCCD3",
    color: "#2E4148",
    fontWeight: "700",
    boxShadow: "0 8px 24px rgba(46,65,72,.2)",
    cursor: "pointer"
  });

  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".html,text/html";
  input.hidden = true;
  button.addEventListener("click", () => input.click());
  input.addEventListener("change", async () => {
    const file = input.files && input.files[0];
    if (!file) return;
    const content = await file.text();
    window.postMessage({ source: "ocean-robot-wechat", type: "SET_CONTENT", html: content }, "*");
    input.value = "";
  });

  window.addEventListener("message", (event) => {
    if (event.source !== window || event.data?.source !== "ocean-robot-wechat-bridge") return;
    button.textContent = event.data.ok ? "已导入 ✓" : "导入失败：编辑器未就绪";
    setTimeout(() => { button.textContent = "导入海机协推文"; }, 2600);
  });

  document.documentElement.append(input, button);
})();
