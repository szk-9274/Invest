import React from 'react';


type IconProps = React.SVGProps<SVGSVGElement> & { size?: number };


const Svg = ({ size = 20, children, ...rest }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...rest}>
    {children}
  </svg>
);


/* ロゴ（左上の蝶/クローバー風） */
export const LogoGlyph: React.FC<{ size?: number }> = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <defs>
      <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#2fd1ff"/>
        <stop offset="1" stopColor="#5ae6ff"/>
      </linearGradient>
    </defs>
    <g fill="url(#lg)">
      <path d="M9.6 2.5c-2.5 0-4.6 2-4.6 4.6 0 1.8 1.1 3.1 2.6 4.2L12 7.2C11.7 4.9 10.7 2.5 9.6 2.5z"/>
      <path d="M14.4 2.5c2.5 0 4.6 2 4.6 4.6 0 1.8-1.1 3.1-2.6 4.2L12 7.2c.3-2.3 1.3-4.7 2.4-4.7z"/>
      <path d="M9.6 21.5c-2.5 0-4.6-2-4.6-4.6 0-1.8 1.1-3.1 2.6-4.2L12 16.8c-.3 2.3-1.3 4.7-2.4 4.7z"/>
      <path d="M14.4 21.5c2.5 0 4.6-2 4.6-4.6 0-1.8-1.1-3.1-2.6-4.2L12 16.8c.3 2.3 1.3 4.7 2.4 4.7z"/>
    </g>
  </svg>
);


export const IconHome = (p: IconProps) => (
  <Svg {...p}><path d="M3 11.5 12 4l9 7.5"/><path d="M6 10.5V19h12v-8.5"/></Svg>
);
export const IconShield = (p: IconProps) => (
  <Svg {...p}><path d="M12 3l8 3v6c0 4.5-3.5 8.5-8 9-4.5-.5-8-4.5-8-9V6l8-3z"/></Svg>
);
export const IconStorage = (p: IconProps) => (
  <Svg {...p}><rect x="3" y="5" width="18" height="6" rx="2"/><rect x="3" y="13" width="18" height="6" rx="2"/><circle cx="7" cy="8" r="1.5"/><circle cx="7" cy="16" r="1.5"/></Svg>
);
export const IconApps = (p: IconProps) => (
  <Svg {...p}><rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/></Svg>
);
export const IconToolbox = (p: IconProps) => (
  <Svg {...p}><rect x="3" y="8" width="18" height="10" rx="2"/><path d="M8 8V6h8v2"/><path d="M10 12h4"/></Svg>
);
export const IconRestore = (p: IconProps) => (
  <Svg {...p}><path d="M4 10a8 8 0 1 1 2.3 5.7"/><path d="M4 10V5m0 5h5"/></Svg>
);
export const IconSettings = (p: IconProps) => (
  <Svg {...p}><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M3.5 7l2.6 1.5M17.9 15.5l2.6 1.5M2 12h3M19 12h3M6.1 18.9l2.1-2.1M15.8 7.2l2.1-2.1"/></Svg>
);
export const IconFeedback = (p: IconProps) => (
  <Svg {...p}><path d="M4 4h16v12H7l-3 3V4z"/><path d="M9 8h6M9 12h4"/></Svg>
);


/* コンテンツ内 */
export const IconBulb = (p: IconProps) => (
  <Svg {...p}><path d="M8 14c-1.3-1.2-2-2.8-2-4.5A6 6 0 1 1 20 9.5c0 1.7-.7 3.3-2 4.5"/><rect x="9" y="15" width="6" height="2" rx="1"/><path d="M10 19h4"/></Svg>
);
export const IconSpark = (p: IconProps) => (
  <Svg {...p}><path d="M12 2l1.8 4.2L18 8l-4.2 1.8L12 14l-1.8-4.2L6 8l4.2-1.8L12 2z"/></Svg>
);
export const IconRocket = (p: IconProps) => (
  <Svg {...p}><path d="M14 10l-4 4"/><path d="M12 2c2.8 1 5.2 3.4 6.2 6.2-2.9 1.3-6.6 4.9-7.9 7.8-2.8-1-5.2-3.4-6.2-6.2C7.1 7.1 10.7 3.3 12 2z"/><path d="M7 17l-2 5 5-2"/></Svg>
);
export const IconCheckBadge = (p: IconProps) => (
  <Svg {...p}><circle cx="12" cy="12" r="8"/><path d="M8 12l2.5 2.5L16 9"/></Svg>
);
export const IconCpu = (p: IconProps) => (
  <Svg {...p}><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/></Svg>
);
export const IconBroom = (p: IconProps) => (
  <Svg {...p}><path d="M3 21l6-6 4 4-6 2H3z"/><path d="M14 14l7-7"/><path d="M17 4l3 3"/></Svg>
);
export const IconPower = (p: IconProps) => (
  <Svg {...p}><path d="M12 2v8"/><path d="M6.2 6.2a7 7 0 1 0 11.6 0"/></Svg>
);

/* 丸まった矢印（リロード） */
export const IconRefresh = (p: IconProps) => (
  <Svg {...p}>
    <path d="M20 11a8 8 0 1 1-3.4-6.4"/>
    <path d="M20 4v6h-6"/>
  </Svg>
);