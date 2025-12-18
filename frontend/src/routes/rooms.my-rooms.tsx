import { createFileRoute } from "@tanstack/react-router";
import { MyRoomsPage } from "../pages/MyRoomsPage";

export const Route = createFileRoute("/rooms/my-rooms")({
  component: MyRoomsPage,
});

