import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { authService } from "../features/auth/services/authService";
import { friendService } from "../features/friends/services/friendService";
import { PageTransition } from "../components/PageTransition";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { UserPlus, Users, Check, X, MessageSquare, Trash2, Ban, Search } from "lucide-react";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";

export const Route = createFileRoute("/friends")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  component: FriendsComponent,
});

function FriendsComponent() {
  const queryClient = useQueryClient();
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [friendIdInput, setFriendIdInput] = useState("");
  const [removingFriendId, setRemovingFriendId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch friends
  const { data: friendsData } = useQuery({
    queryKey: ["friends"],
    queryFn: async () => {
      const response = await friendService.getFriends();
      return response.status === "success" ? response.data : { friends: [], total: 0 };
    },
  });

  // Fetch received requests
  const { data: receivedRequests = [] } = useQuery({
    queryKey: ["friend-requests", "received"],
    queryFn: async () => {
      const response = await friendService.getReceivedRequests(false);
      return response.status === "success" ? response.data : [];
    },
  });

  // Fetch sent requests
  const { data: sentRequests = [] } = useQuery({
    queryKey: ["friend-requests", "sent"],
    queryFn: async () => {
      const response = await friendService.getSentRequests();
      return response.status === "success" ? response.data : [];
    },
  });

  // Send friend request
  const sendRequestMutation = useMutation({
    mutationFn: (receiverId: string) => friendService.sendFriendRequest(receiverId),
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["friend-requests", "sent"] });
        toast.success("친구 요청을 보냈습니다");
        setIsAddDialogOpen(false);
        setFriendIdInput("");
      } else {
        toast.error(response.error?.message || "친구 요청 전송 실패");
      }
    },
  });

  // Accept friend request
  const acceptRequestMutation = useMutation({
    mutationFn: (requestId: string) => friendService.acceptFriendRequest(requestId),
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["friend-requests", "received"] });
        queryClient.invalidateQueries({ queryKey: ["friends"] });
        toast.success("친구 요청을 수락했습니다");
      } else {
        toast.error(response.error?.message || "요청 수락 실패");
      }
    },
  });

  // Reject friend request
  const rejectRequestMutation = useMutation({
    mutationFn: (requestId: string) => friendService.rejectFriendRequest(requestId),
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["friend-requests", "received"] });
        toast.success("친구 요청을 거절했습니다");
      } else {
        toast.error(response.error?.message || "요청 거절 실패");
      }
    },
  });

  // Remove friend
  const removeFriendMutation = useMutation({
    mutationFn: (friendId: string) => friendService.removeFriend(friendId),
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["friends"] });
        toast.success("친구를 삭제했습니다");
        setRemovingFriendId(null);
      } else {
        toast.error(response.error?.message || "친구 삭제 실패");
      }
    },
  });

  const friends = friendsData?.friends || [];
  const filteredFriends = friends.filter((friend) =>
    friend.friend_username.toLowerCase().includes(searchQuery.toLowerCase())
  );
  const pendingReceivedRequests = receivedRequests.filter((req) => req.status === "pending");

  return (
    <PageTransition>
      <div className="container mx-auto p-6 max-w-6xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              친구
            </h1>
            <p className="text-muted-foreground mt-1">
              친구와 함께 집중하고 성장하세요
            </p>
          </div>
          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <UserPlus className="w-4 h-4" />
                친구 추가
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>친구 추가</DialogTitle>
                <DialogDescription>
                  사용자 ID를 입력하여 친구 요청을 보내세요
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <Input
                  placeholder="사용자 ID 입력"
                  value={friendIdInput}
                  onChange={(e) => setFriendIdInput(e.target.value)}
                />
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setIsAddDialogOpen(false)}
                  >
                    취소
                  </Button>
                  <Button
                    onClick={() => sendRequestMutation.mutate(friendIdInput)}
                    disabled={!friendIdInput.trim() || sendRequestMutation.isPending}
                  >
                    요청 보내기
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <Tabs defaultValue="friends" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="friends" className="gap-2">
              <Users className="w-4 h-4" />
              친구 목록
              <Badge variant="secondary">{friends.length}</Badge>
            </TabsTrigger>
            <TabsTrigger value="received" className="gap-2">
              받은 요청
              {pendingReceivedRequests.length > 0 && (
                <Badge className="bg-red-500">{pendingReceivedRequests.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="sent" className="gap-2">
              보낸 요청
              <Badge variant="secondary">{sentRequests.length}</Badge>
            </TabsTrigger>
          </TabsList>

          {/* Friends List */}
          <TabsContent value="friends" className="space-y-4">
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="친구 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {filteredFriends.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <Users className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
                  <p className="text-muted-foreground">
                    {searchQuery ? "검색 결과가 없습니다" : "아직 친구가 없습니다"}
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {filteredFriends.map((friend) => (
                  <Card key={friend.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Avatar className="w-12 h-12">
                            <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white">
                              {friend.friend_username.slice(0, 2).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <h3 className="font-semibold">{friend.friend_username}</h3>
                            {friend.friend_bio && (
                              <p className="text-sm text-muted-foreground">
                                {friend.friend_bio}
                              </p>
                            )}
                            <div className="flex items-center gap-2 mt-1">
                              <div
                                className={`w-2 h-2 rounded-full ${
                                  friend.friend_is_online ? "bg-green-500" : "bg-gray-400"
                                }`}
                              />
                              <span className="text-xs text-muted-foreground">
                                {friend.friend_is_online ? "온라인" : "오프라인"}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="gap-2">
                            <MessageSquare className="w-4 h-4" />
                            메시지
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setRemovingFriendId(friend.friend_id)}
                          >
                            <Trash2 className="w-4 h-4 text-destructive" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Received Requests */}
          <TabsContent value="received" className="space-y-4">
            {pendingReceivedRequests.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <UserPlus className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
                  <p className="text-muted-foreground">받은 친구 요청이 없습니다</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {pendingReceivedRequests.map((request) => (
                  <Card key={request.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Avatar className="w-10 h-10">
                            <AvatarFallback>
                              {request.sender_username?.slice(0, 2).toUpperCase() || "?"}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <h4 className="font-medium">
                              {request.sender_username || "알 수 없음"}
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              {formatDistanceToNow(new Date(request.created_at), {
                                addSuffix: true,
                                locale: ko,
                              })}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => acceptRequestMutation.mutate(request.id)}
                            disabled={acceptRequestMutation.isPending}
                            className="gap-1"
                          >
                            <Check className="w-4 h-4" />
                            수락
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => rejectRequestMutation.mutate(request.id)}
                            disabled={rejectRequestMutation.isPending}
                            className="gap-1"
                          >
                            <X className="w-4 h-4" />
                            거절
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Sent Requests */}
          <TabsContent value="sent" className="space-y-4">
            {sentRequests.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <UserPlus className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
                  <p className="text-muted-foreground">보낸 친구 요청이 없습니다</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {sentRequests.map((request) => (
                  <Card key={request.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Avatar className="w-10 h-10">
                            <AvatarFallback>
                              {request.receiver_username?.slice(0, 2).toUpperCase() || "?"}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <h4 className="font-medium">
                              {request.receiver_username || "알 수 없음"}
                            </h4>
                            <div className="flex items-center gap-2">
                              <Badge
                                variant={
                                  request.status === "pending"
                                    ? "secondary"
                                    : request.status === "accepted"
                                      ? "default"
                                      : "destructive"
                                }
                              >
                                {request.status === "pending"
                                  ? "대기중"
                                  : request.status === "accepted"
                                    ? "수락됨"
                                    : "거절됨"}
                              </Badge>
                              <span className="text-sm text-muted-foreground">
                                {formatDistanceToNow(new Date(request.created_at), {
                                  addSuffix: true,
                                  locale: ko,
                                })}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Remove Friend Confirmation */}
        <AlertDialog
          open={!!removingFriendId}
          onOpenChange={() => setRemovingFriendId(null)}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>친구 삭제</AlertDialogTitle>
              <AlertDialogDescription>
                정말 이 친구를 삭제하시겠습니까? 이 작업은 취소할 수 없습니다.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>취소</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => {
                  if (removingFriendId) {
                    removeFriendMutation.mutate(removingFriendId);
                  }
                }}
                className="bg-destructive hover:bg-destructive/90"
              >
                삭제
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </PageTransition>
  );
}
