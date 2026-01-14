import { heroui } from "@heroui/react";

export default heroui({
  themes: {
    "flexoki-dark": {
      extend: "dark",
      colors: {
        // Primary (cyan - links, active states)
        primary: {
          50: "#122F2C",
          100: "#143F3C",
          200: "#164F4A",
          300: "#1C6C66",
          400: "#24837B",
          500: "#2F968D",
          600: "#3AA99F", // cyan-400 (main for dark)
          700: "#5ABDAC",
          800: "#87D3C3",
          900: "#DDF1E4",
          DEFAULT: "#3AA99F",
          foreground: "#000000",
        },

        // Secondary (purple)
        secondary: {
          50: "#1A1623",
          100: "#261C39",
          200: "#31234E",
          300: "#3C2A62",
          400: "#4F3685",
          500: "#5E409D",
          600: "#735EB5",
          700: "#8B7EC8", // purple-400 (main for dark)
          800: "#A699D0",
          900: "#F0EAEC",
          DEFAULT: "#8B7EC8",
        },

        // Success (green)
        success: {
          50: "#1A1E0C",
          100: "#252D09",
          200: "#313D07",
          300: "#3D4C07",
          400: "#536907",
          500: "#66800B",
          600: "#768D21",
          700: "#879A39", // green-400 (main for dark)
          800: "#A0AF54",
          900: "#EDEECF",
          DEFAULT: "#879A39",
        },

        // Warning (orange)
        warning: {
          50: "#27180E",
          100: "#40200D",
          200: "#59290D",
          300: "#71320D",
          400: "#9D4310",
          500: "#BC5215",
          600: "#CB6120",
          700: "#DA702C", // orange-400 (main for dark)
          800: "#EC8B49",
          900: "#FFE7CE",
          DEFAULT: "#DA702C",
        },

        // Danger (red)
        danger: {
          50: "#261312",
          100: "#3E1715",
          200: "#551B18",
          300: "#6C201C",
          400: "#942822",
          500: "#AF3029",
          600: "#C03E35",
          700: "#D14D41", // red-400 (main for dark)
          800: "#E8705F",
          900: "#FFE1D5",
          DEFAULT: "#D14D41",
        },

        // Focus ring
        focus: "#3AA99F", // cyan-400
      },
    },

    "flexoki-light": {
      extend: "light",
      colors: {
        // Primary (cyan - use 600 for light mode)
        primary: {
          50: "#DDF1E4",
          100: "#BFE8D9",
          200: "#A2DECE",
          300: "#87D3C3",
          400: "#5ABDAC",
          500: "#3AA99F",
          600: "#2F968D",
          700: "#24837B", // cyan-600 (main for light)
          800: "#1C6C66",
          900: "#122F2C",
          DEFAULT: "#24837B",
        },

        // Secondary (purple - use 600 for light mode)
        secondary: {
          50: "#F0EAEC",
          100: "#E2D9E9",
          200: "#D3CAE6",
          300: "#C4B9E0",
          400: "#A699D0",
          500: "#8B7EC8",
          600: "#735EB5",
          700: "#5E409D", // purple-600 (main for light)
          800: "#4F3685",
          900: "#1A1623",
          DEFAULT: "#5E409D",
        },

        // Success (green - use 600 for light mode)
        success: {
          50: "#EDEECF",
          100: "#DDE2B2",
          200: "#CDD597",
          300: "#BEC97E",
          400: "#A0AF54",
          500: "#879A39",
          600: "#768D21",
          700: "#66800B", // green-600 (main for light)
          800: "#536907",
          900: "#1A1E0C",
          DEFAULT: "#66800B",
        },

        // Warning (orange - use 600 for light mode)
        warning: {
          50: "#FFE7CE",
          100: "#FED3AF",
          200: "#FCC192",
          300: "#F9AE77",
          400: "#EC8B49",
          500: "#DA702C",
          600: "#CB6120",
          700: "#BC5215", // orange-600 (main for light)
          800: "#9D4310",
          900: "#27180E",
          DEFAULT: "#BC5215",
        },

        // Danger (red - use 600 for light mode)
        danger: {
          50: "#FFE1D5",
          100: "#FFCABB",
          200: "#FDB2A2",
          300: "#F89A8A",
          400: "#E8705F",
          500: "#D14D41",
          600: "#C03E35",
          700: "#AF3029", // red-600 (main for light)
          800: "#942822",
          900: "#261312",
          DEFAULT: "#AF3029",
        },
        // Focus ring
        focus: "#24837B", // cyan-600
      },
    },
  },
});
