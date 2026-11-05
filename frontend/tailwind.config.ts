import type { Config } from "tailwindcss";

// Pastel theme (user direction, 2026-11-05). Each pastel has a soft fill, a mid tone for
// charts and dots, and a dark ink for text on the soft fill, so labels keep enough contrast.
const pastel = (soft: string, mid: string, ink: string) => ({ soft, mid, ink, DEFAULT: mid });

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["var(--font-plex)", "system-ui", "sans-serif"] },
      borderRadius: { DEFAULT: "4px", md: "6px" },
      colors: {
        canvas: "#E4EAF1",
        surface: "#FFFFFF",
        subtle: "#F6F7FB",
        line: "#E5E8EF",
        ink: { DEFAULT: "#1E2333", muted: "#5C6478", faint: "#9AA1B2" },
        brand: { DEFAULT: "#5B4BC4", hover: "#4A3BAE", soft: "#EEEBFC" },
        lavender: pastel("#EFEBFE", "#B9A8F5", "#5B3FC4"),
        mint: pastel("#E3F7EC", "#8EDBB0", "#16774A"),
        peach: pastel("#FEEEE2", "#F7B98C", "#A44A12"),
        sky: pastel("#E3F1FD", "#94C8F2", "#1F5F96"),
        rose: pastel("#FDE8EC", "#F2A3B3", "#A62B47"),
        butter: pastel("#FDF6D8", "#F0D46A", "#7C5E05"),
        // Semantic roles map to pastels: info = sky, success = mint, caution = peach, danger = rose.
        info: { DEFAULT: "#4B8FD6", soft: "#E3F1FD", ink: "#1F5F96" },
        success: { DEFAULT: "#3BAF74", soft: "#E3F7EC", ink: "#16774A" },
        caution: { DEFAULT: "#E58A43", soft: "#FEEEE2", ink: "#A44A12" },
        danger: { DEFAULT: "#E0607A", soft: "#FDE8EC", ink: "#A62B47" },
      },
      fontSize: { xs: ["12px", "16px"], sm: ["13px", "18px"], base: ["14px", "20px"] },
      boxShadow: { card: "0 1px 2px rgba(30, 35, 51, 0.04)", lift: "0 4px 14px rgba(30, 35, 51, 0.08)" },
    },
  },
  plugins: [],
};
export default config;
