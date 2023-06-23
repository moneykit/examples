type Theme = {
    colors: ThemeColors;
    typography: ThemeTypography;
    spacing: ThemeSpacing;
    components: ThemeComponents;
    screens: ThemeScreens;
    modal: ThemeModal;
    popover: ThemePopover;
};
type ThemeAppearanceBasedValue<T> = {
    light: T;
    dark: T;
};
type ThemeSize = string;
type ThemeFontFamily = string;
type ThemeBorderRadius = string;
type ThemeColor = string;
type ThemeDynamicColor = ThemeColor | ThemeAppearanceBasedValue<ThemeColor>;
type ThemeBoxShadow = string;
type ThemeDynamicBoxShadow = ThemeBoxShadow | ThemeAppearanceBasedValue<ThemeBoxShadow>;
type ThemeBorder = string;
type ThemeDynamicBorder = ThemeBorder | ThemeAppearanceBasedValue<ThemeBorder>;
type ThemeBackdropFilter = string;
type ThemeDynamicBackdropFilter = ThemeBackdropFilter | ThemeAppearanceBasedValue<ThemeBackdropFilter>;
type ThemeModal = {
    borderRadius: ThemeBorderRadius | null;
    boxShadow: ThemeDynamicBoxShadow | null;
    overlayBackgroundColor: ThemeDynamicColor | null;
    overlayBackdropFilter: ThemeDynamicBackdropFilter | null;
};
type ThemePopover = {
    borderRadius: ThemeBorderRadius | null;
    boxShadow: ThemeDynamicBoxShadow | null;
};
type ThemeColors = {
    accent: ThemeDynamicColor;
    primaryBackground: ThemeDynamicColor;
    secondaryBackground: ThemeDynamicColor;
    primaryContent: ThemeDynamicColor;
    secondaryContent: ThemeDynamicColor;
    primaryForeground: ThemeDynamicColor;
    secondaryForeground: ThemeDynamicColor;
    tertiaryForeground: ThemeDynamicColor;
    primaryFill: ThemeDynamicColor;
    secondaryFill: ThemeDynamicColor;
    tertiaryFill: ThemeDynamicColor;
    success: ThemeDynamicColor;
    warning: ThemeDynamicColor;
    error: ThemeDynamicColor;
    separator: ThemeDynamicColor;
    selection: ThemeDynamicColor;
};
type ThemeTypography = {
    fontFamily: ThemeFontFamily;
    largeTitle: ThemeTypographyStyle;
    title1: ThemeTypographyStyle;
    title2: ThemeTypographyStyle;
    title3: ThemeTypographyStyle;
    body: ThemeTypographyStyle;
    smallBody: ThemeTypographyStyle;
    button: ThemeTypographyStyle;
    input: ThemeTypographyStyle;
};
declare enum ThemeTypographyTextStyle {
    largeTitle = 0,
    title1 = 1,
    title2 = 2,
    title3 = 3,
    body = 4,
    smallBody = 5,
    button = 6,
    input = 7
}
type ThemeTypographyStyle = {
    size: string;
    lineHeight: string;
    letterSpacing: string;
    weight: ThemeTypographyWeight;
};
type ThemeTypographyWeight = "normal" | "bold" | "lighter" | "bolder" | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | "inherit" | "initial" | "revert" | "revert-layer" | "unset";
type ThemeSpacing = {
    contentHorizontalInset: string;
    buttonHorizontalInset: string;
};
type ThemeComponents = {
    navigationBar: ThemeComponentsNavigationBar;
    contentView: ThemeComponentsContentView;
    buttonPrimary: ThemeComponentsButton;
    searchBar: ThemeComponentsSearchBar;
    textField: ThemeComponentsTextField;
};
type ThemeComponentsNavigationBar = {
    height: string;
};
type ThemeComponentsContentView = {
    borderRadius: ThemeBorderRadius;
    boxShadow: ThemeDynamicBoxShadow | null;
    border: ThemeDynamicBorder | null;
};
type ThemeComponentsButton = {
    height: ThemeSize;
    borderRadius: ThemeBorderRadius;
};
type ThemeComponentsSearchBar = {
    height: ThemeSize;
    borderRadius: ThemeBorderRadius;
};
type ThemeComponentsTextField = {
    height: ThemeSize;
    borderRadius: ThemeBorderRadius;
};
type ThemeScreens = {
    finder: ThemeScreensFinder;
};
type ThemeScreensFinder = {
    title: string;
    subtitle: string | null;
    searchPlaceholder: string;
    institutionCellBoxShadow: ThemeDynamicBoxShadow | null;
    institutionCellBorderRadius: ThemeBorderRadius;
    institutionCellBorder: ThemeDynamicBorder | null;
    institutionCellSpacing: string;
    institutionCellBackgroundColor: ThemeDynamicColor | null;
};

export { Theme, ThemeAppearanceBasedValue, ThemeBackdropFilter, ThemeBorder, ThemeBorderRadius, ThemeBoxShadow, ThemeColor, ThemeColors, ThemeComponents, ThemeComponentsButton, ThemeComponentsContentView, ThemeComponentsNavigationBar, ThemeComponentsSearchBar, ThemeComponentsTextField, ThemeDynamicBackdropFilter, ThemeDynamicBorder, ThemeDynamicBoxShadow, ThemeDynamicColor, ThemeFontFamily, ThemeModal, ThemePopover, ThemeScreens, ThemeScreensFinder, ThemeSize, ThemeSpacing, ThemeTypography, ThemeTypographyStyle, ThemeTypographyTextStyle, ThemeTypographyWeight };
