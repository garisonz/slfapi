import type { ButtonHTMLAttributes } from "react";

export default function Button({
  type = "button",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button type={type} {...props} />;
}
