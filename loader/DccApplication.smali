.class public Ldex2c/loader/DccApplication;
.super Landroid/app/Application;


# direct methods
.method static constructor <clinit>()V
    .registers 1
    invoke-static {}, Ldex2c/loader/DccApplication;->getContext()Landroid/content/Context;

    move-result-object v0

    invoke-static {v0}, Ldex2c/loader/NativeLibLoader;->loadNativeLib(Landroid/content/Context;)V

    return-void
.end method

.method public native constructor <init>()V
.end method

.method public static getContext()Landroid/content/Context;
    .registers 9

    const/4 v0, 0x0
    :try_start_1
    const-string v1, "android.app.ActivityThread"

    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v1
    const-string v2, "currentActivityThread"

    const/4 v3, 0x0

    new-array v4, v3, [Ljava/lang/Class;

    invoke-virtual {v1, v2, v4}, Ljava/lang/Class;->getDeclaredMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v2

    const/4 v4, 0x1
    invoke-virtual {v2, v4}, Ljava/lang/reflect/Method;->setAccessible(Z)V
    new-array v5, v3, [Ljava/lang/Object;

    invoke-virtual {v2, v0, v5}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2
    const-string v5, "mBoundApplication"

    invoke-virtual {v1, v5}, Ljava/lang/Class;->getDeclaredField(Ljava/lang/String;)Ljava/lang/reflect/Field;

    move-result-object v5
    invoke-virtual {v5, v4}, Ljava/lang/reflect/Field;->setAccessible(Z)V
    invoke-virtual {v5, v2}, Ljava/lang/reflect/Field;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5
    invoke-virtual {v5}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v6

    const-string v7, "info"

    invoke-virtual {v6, v7}, Ljava/lang/Class;->getDeclaredField(Ljava/lang/String;)Ljava/lang/reflect/Field;

    move-result-object v6
    invoke-virtual {v6, v4}, Ljava/lang/reflect/Field;->setAccessible(Z)V
    invoke-virtual {v6, v5}, Ljava/lang/reflect/Field;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5
    const-string v6, "android.app.ContextImpl"

    invoke-static {v6}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v6

    const-string v7, "createAppContext"

    const/4 v8, 0x2

    new-array v8, v8, [Ljava/lang/Class;

    aput-object v1, v8, v3

    invoke-virtual {v5}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v1

    aput-object v1, v8, v4

    invoke-virtual {v6, v7, v8}, Ljava/lang/Class;->getDeclaredMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v1
    invoke-virtual {v1, v4}, Ljava/lang/reflect/Method;->setAccessible(Z)V
    filled-new-array {v2, v5}, [Ljava/lang/Object;

    move-result-object v2

    invoke-virtual {v1, v0, v2}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1
    instance-of v2, v1, Landroid/content/Context;

    if-eqz v2, :cond_6d
    check-cast v1, Landroid/content/Context;
    :try_end_60
    .catch Ljava/lang/ClassNotFoundException; {:try_start_1 .. :try_end_60} :catch_69
    .catch Ljava/lang/IllegalAccessException; {:try_start_1 .. :try_end_60} :catch_67
    .catch Ljava/lang/NoSuchFieldException; {:try_start_1 .. :try_end_60} :catch_65
    .catch Ljava/lang/NoSuchMethodException; {:try_start_1 .. :try_end_60} :catch_63
    .catch Ljava/lang/reflect/InvocationTargetException; {:try_start_1 .. :try_end_60} :catch_61

    return-object v1

    :catch_61
    move-exception v1

    goto :goto_6a

    :catch_63
    move-exception v1

    goto :goto_6a

    :catch_65
    move-exception v1

    goto :goto_6a

    :catch_67
    move-exception v1

    goto :goto_6a

    :catch_69
    move-exception v1
    :goto_6a
    invoke-virtual {v1}, Ljava/lang/ReflectiveOperationException;->printStackTrace()V

    :cond_6d
    return-object v0
.end method

.method public static final native initDcc()V
.end method
