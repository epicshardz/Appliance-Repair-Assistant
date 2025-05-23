export type ThemeColors = {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  border: string;
};

export const lightTheme: ThemeColors = {
  primary: '#2563eb', // blue-600
  secondary: '#4f46e5', // indigo-600
  background: '#F8FAFC',
  surface: '#F3F4F6',
  text: '#1F2937', // gray-800
  textSecondary: '#64748B', // gray-500
  border: '#E2E8F0', // gray-200
};

export const darkTheme: ThemeColors = {
  primary: '#3B82F6', // blue-500
  secondary: '#6366F1', // indigo-500
  background: '#1E293B', // slate-800
  surface: '#2D3748', // gray-800
  text: '#F8FAFC', // slate-50
  textSecondary: '#94A3B8', // slate-400
  border: '#475569', // slate-600
};

// Function to convert hex to RGB for CSS variables
export function hexToRGB(hex: string): { r: number; g: number; b: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 0, g: 0, b: 0 };
}

// Function to apply theme to CSS variables
export function applyTheme(theme: ThemeColors) {
  const root = document.documentElement;
  Object.entries(theme).forEach(([key, value]) => {
    const rgb = hexToRGB(value);
    root.style.setProperty(`--${key}-rgb`, `${rgb.r}, ${rgb.g}, ${rgb.b}`);
  });
}
