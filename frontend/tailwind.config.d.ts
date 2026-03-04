declare const _default: {
    content: string[];
    theme: {
        extend: {
            colors: {
                elder: {
                    critical: string;
                    warning: string;
                    ok: string;
                    action: string;
                    'critical-bg': string;
                    'warning-bg': string;
                    'ok-bg': string;
                    'action-bg': string;
                    surface: string;
                    'surface-alt': string;
                    border: string;
                    'text-primary': string;
                    'text-secondary': string;
                    'text-muted': string;
                };
            };
            fontFamily: {
                sans: [string, string, string, string];
                mono: [string, string, string];
            };
            fontSize: {
                'room-number': [string, {
                    lineHeight: string;
                    fontWeight: string;
                }];
                'alert-title': [string, {
                    lineHeight: string;
                    fontWeight: string;
                }];
            };
            spacing: {
                'sidebar-w': string;
                'sidebar-collapsed': string;
                'bottom-nav': string;
                'topbar-h': string;
            };
            animation: {
                'pulse-critical': string;
                'fade-in': string;
                'slide-up': string;
            };
            keyframes: {
                fadeIn: {
                    '0%': {
                        opacity: string;
                    };
                    '100%': {
                        opacity: string;
                    };
                };
                slideUp: {
                    '0%': {
                        opacity: string;
                        transform: string;
                    };
                    '100%': {
                        opacity: string;
                        transform: string;
                    };
                };
            };
        };
    };
    plugins: never[];
};
export default _default;
