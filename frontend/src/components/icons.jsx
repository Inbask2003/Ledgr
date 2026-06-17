function Icon({ children, className = "h-5 w-5", ...props }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      {children}
    </svg>
  );
}

export const HomeIcon = (p) => (
  <Icon {...p}>
    <path d="M3 10.5 12 3l9 7.5" />
    <path d="M5 9.5V21h14V9.5" />
    <path d="M9 21v-6h6v6" />
  </Icon>
);

export const CardIcon = (p) => (
  <Icon {...p}>
    <rect x="2.5" y="5" width="19" height="14" rx="2.5" />
    <path d="M2.5 9.5h19" />
    <path d="M6 14.5h4" />
  </Icon>
);

export const LedgerIcon = (p) => (
  <Icon {...p}>
    <path d="M5 4h12a2 2 0 0 1 2 2v14H7a2 2 0 0 1-2-2z" />
    <path d="M5 4a2 2 0 0 0-2 2v12" />
    <path d="M9 8h6M9 12h6" />
  </Icon>
);

export const PlusIcon = (p) => (
  <Icon {...p}>
    <path d="M12 5v14M5 12h14" />
  </Icon>
);

export const DownloadIcon = (p) => (
  <Icon {...p}>
    <path d="M12 3v12" />
    <path d="m7 11 5 5 5-5" />
    <path d="M5 21h14" />
  </Icon>
);

export const ArrowLeftIcon = (p) => (
  <Icon {...p}>
    <path d="M19 12H5" />
    <path d="m12 19-7-7 7-7" />
  </Icon>
);

export const WalletIcon = (p) => (
  <Icon {...p}>
    <path d="M3 7a2 2 0 0 1 2-2h12v4" />
    <rect x="3" y="7" width="18" height="13" rx="2.5" />
    <path d="M16 13h2" />
  </Icon>
);

export const ReceiptIcon = (p) => (
  <Icon {...p}>
    <path d="M5 3v18l2-1.5L9 21l2-1.5L13 21l2-1.5L17 21l2-1.5V3l-2 1.5L15 3l-2 1.5L11 3 9 4.5 7 3z" />
    <path d="M9 8h6M9 12h6" />
  </Icon>
);

export const ActivityIcon = (p) => (
  <Icon {...p}>
    <path d="M3 12h4l2.5 7 5-14L17 12h4" />
  </Icon>
);

export const WebhookIcon = (p) => (
  <Icon {...p}>
    <path d="M12 3a4 4 0 0 0-3.5 6l-2.5 4.3" />
    <path d="M5 14a4 4 0 1 0 4 4h5" />
    <path d="M15.5 9a4 4 0 1 1 3 7l-2.5-4.3" />
  </Icon>
);

export const KeyIcon = (p) => (
  <Icon {...p}>
    <circle cx="7.5" cy="15.5" r="4.5" />
    <path d="m10.5 12.5 8-8" />
    <path d="m16 4.5 3 3" />
    <path d="m13.5 7 3 3" />
  </Icon>
);

export const CopyIcon = (p) => (
  <Icon {...p}>
    <rect x="9" y="9" width="11" height="11" rx="2" />
    <path d="M5 15V5a2 2 0 0 1 2-2h10" />
  </Icon>
);

export const LogoutIcon = (p) => (
  <Icon {...p}>
    <path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3" />
    <path d="M10 17l-5-5 5-5" />
    <path d="M5 12h12" />
  </Icon>
);
