import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ErrorDialog from "../ErrorDialog";

describe("ErrorDialog", () => {
  it("renders code, title, description, severity badge", () => {
    render(
      <ErrorDialog
        code="0x80FU"
        title="Stack Overflowed Into the Carpet"
        description="The kernel attempted to fold itself but ran out of corners."
        severity="ERROR"
        subsystem="kernel.mood"
      />
    );

    expect(screen.getByText("0x80FU")).toBeInTheDocument();
    expect(screen.getByText(/Stack Overflowed Into the Carpet/)).toBeInTheDocument();
    expect(screen.getByText(/ran out of corners/)).toBeInTheDocument();
    expect(screen.getByText("ERROR")).toBeInTheDocument();
  });
});
