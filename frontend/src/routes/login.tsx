import { createFileRoute, redirect } from '@tanstack/react-router';
import { AuthPage } from '../pages/Auth';
import { PageTransition } from '../components/PageTransition';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useNavigate } from '@tanstack/react-router';
import { authService } from '../features/auth/services/authService';

export const Route = createFileRoute('/login')({
  beforeLoad: () => {
    // 이미 로그인된 경우 홈으로 리다이렉트
    if (authService.isAuthenticated()) {
      throw redirect({ to: '/' });
    }
  },
  component: LoginComponent,
});

function LoginComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: (data: { email: string; password: string }) =>
      authService.login(data),
    onSuccess: (response) => {
      if (response.status === 'success') {
        queryClient.invalidateQueries();
        navigate({ to: '/' });
        toast.success('로그인 성공!');
      } else {
        toast.error(response.error?.message || '로그인에 실패했습니다');
      }
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : '로그인에 실패했습니다');
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: { email: string; password: string; username: string }) =>
      authService.register(data),
    onSuccess: (response) => {
      if (response.status === 'success') {
        queryClient.invalidateQueries();
        navigate({ to: '/' });
        toast.success('회원가입 성공! Focus Mate에 오신 것을 환영합니다.');
      } else {
        toast.error(response.error?.message || '회원가입에 실패했습니다');
      }
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : '회원가입에 실패했습니다');
    },
  });

  const handleLogin = (email: string, password: string) => {
    loginMutation.mutate({ email, password });
  };

  const handleSignup = (email: string, password: string, name: string) => {
    registerMutation.mutate({ email, password, username: name });
  };

  return (
    <PageTransition>
      <AuthPage
        onLogin={handleLogin}
        onSignup={handleSignup}
        isLoading={loginMutation.isPending || registerMutation.isPending}
      />
    </PageTransition>
  );
}

