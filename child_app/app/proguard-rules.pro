# PARENTIQ Child Companion Proguard Rules
-keepattributes *Annotation*
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}
-keep class com.parentiq.child.data.models.** { *; }

