// Render CountOutput as a frequency badge with the integer result.
// The count is shown prominently so the dialect frequency is immediately readable.
import { h } from "./kit/components.js";

export default {
  CountOutput: (output) =>
    h("div", {}, [
      h("p", { text: "Occurrences found:" }),
      h("span", { text: String(output.count), style: "font-size:2rem;font-weight:bold;font-family:monospace;" }),
    ]),
};
