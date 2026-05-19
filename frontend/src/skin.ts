import { createContext } from "react";

export type Skin = "win98" | "aqua" | "terminal" | "ios";

export const SkinContext = createContext<{ skin: Skin; setSkin: (s: Skin) => void }>({
  skin: "win98",
  setSkin: () => {},
});
