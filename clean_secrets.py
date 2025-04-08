from git_filter_repo import Filter

class SecretRemover(Filter):
    def commit(self, commit):
        # 移除敏感信息
        commit.message = b'Removed sensitive information'
        return True

filter = SecretRemover()
